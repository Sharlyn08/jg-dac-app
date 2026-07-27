import os
import uuid
import json
import sqlite3
import io
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import anthropic
from docx import Document

from kbi_data import PROGRAMS, COMP_META, LEVEL_LABELS, get_activity, build_kbi_prompt, get_comp_order
from docx_generator import generate_activity_document, generate_dac_report

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DB_PATH = os.getenv("DB_PATH", "dac.db")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS candidates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT,
            assessment_date TEXT,
            assessors TEXT,
            program TEXT DEFAULT 'accelerate',
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS activities (
            id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL,
            activity_code TEXT NOT NULL,
            transcript_filename TEXT,
            transcript_path TEXT,
            analysis_json TEXT,
            confirmed_json TEXT,
            status TEXT DEFAULT 'pending',
            error_msg TEXT,
            created_at TEXT,
            analyzed_at TEXT,
            confirmed_at TEXT,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        );
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
templates.env.cache = None  # Disable LRU cache — prevents unhashable dict error
templates = Jinja2Templates(directory="templates")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def extract_docx_text(path: str) -> str:
    doc = Document(path)
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(lines)


def get_candidate_with_activities(candidate_id: str) -> dict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM candidates WHERE id=?", (candidate_id,)).fetchone()
    if not row:
        conn.close()
        return None
    cand = dict(row)
    acts = conn.execute(
        "SELECT * FROM activities WHERE candidate_id=? ORDER BY created_at",
        (candidate_id,)
    ).fetchall()
    conn.close()
    cand["activities"] = {a["activity_code"]: dict(a) for a in acts}
    return cand


def activity_status_label(status: str) -> str:
    return {
        "pending": "Pending",
        "uploaded": "Transcript uploaded",
        "analyzing": "Analyzing…",
        "ready": "Ready to verify",
        "confirmed": "Confirmed",
        "error": "Error",
    }.get(status, status)


templates.env.globals["activity_status_label"] = activity_status_label
templates.env.filters["fromjson"] = json.loads


def _ctx(request: Request, **kwargs) -> dict:
    """Build template context with shared data included."""
    return {
        "request": request,
        "PROGRAMS": PROGRAMS,
        "COMP_META": COMP_META,
        "LEVEL_LABELS": LEVEL_LABELS,
        **kwargs,
    }


def get_or_create_activity(conn, candidate_id: str, activity_code: str, program: str) -> dict:
    row = conn.execute(
        "SELECT * FROM activities WHERE candidate_id=? AND activity_code=?",
        (candidate_id, activity_code)
    ).fetchone()
    if row:
        return dict(row)
    act_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO activities (id, candidate_id, activity_code, status, created_at) VALUES (?,?,?,?,?)",
        (act_id, candidate_id, activity_code, "pending", datetime.utcnow().isoformat())
    )
    conn.commit()
    return {"id": act_id, "candidate_id": candidate_id, "activity_code": activity_code, "status": "pending"}


# ---------------------------------------------------------------------------
# AI Analysis
# ---------------------------------------------------------------------------
ANALYSIS_PROMPT = """You are an expert assessor for the Jollibee Group Development Assessment Center (DAC) {program_name} program.

Your task is to analyze a transcript from the {activity_name} activity and suggest ratings for each KBI based strictly on evidence from the transcript.

CANDIDATE ROLE: {candidate_role}

COMPETENCY AND KBI DEFINITIONS:
{kbi_definitions}

RATING SCALE:
1 - Does Not Demonstrate: Numerous missed opportunities or opposite behaviors; intervention needed
2 - Inconsistently Demonstrates: Some missed opportunities; a few gaps; minimal negative impact
3 - Consistently Demonstrates: Regularly demonstrates the behavior in the expected manner
4 - Exceeds Expectations: Many commendable instances; clearly positive impact on others

RULES:
- Only rate based on what ACTUALLY appears in the transcript
- Evidence must reference specific quotes or behaviors — not general impressions
- Format evidence as: "[Direct quote or paraphrase]" — [explanation of mapping to this KBI]
- Mixed or inconsistent evidence = Level 2
- Consistently strong throughout = Level 3
- Level 4 requires multiple standout, above-expectation moments
- Level 1 requires notable failures or consistent opposite behaviors
- For group exercises: only assess THIS candidate's specific contributions, not the group overall

TRANSCRIPT:
{transcript_text}

Return ONLY valid JSON (no markdown, no explanation outside the JSON):
{{
  "competencies": {{
    "COMP_CODE": {{
      "kbis": [
        {{
          "n": 1,
          "title": "KBI title",
          "suggested_rating": 2,
          "evidence": "Evidence and explanation"
        }}
      ],
      "overall": 2,
      "rationale": "One-sentence rationale for the overall rating"
    }}
  }}
}}"""


def run_analysis(candidate_id: str, activity_code: str):
    conn = get_db()
    try:
        cand = dict(conn.execute("SELECT * FROM candidates WHERE id=?", (candidate_id,)).fetchone())
        act_row = conn.execute(
            "SELECT * FROM activities WHERE candidate_id=? AND activity_code=?",
            (candidate_id, activity_code)
        ).fetchone()
        if not act_row:
            return
        act = dict(act_row)

        if not act.get("transcript_path") or not os.path.exists(act["transcript_path"]):
            conn.execute(
                "UPDATE activities SET status='error', error_msg=? WHERE id=?",
                ("Transcript file not found.", act["id"])
            )
            conn.commit()
            return

        transcript_text = extract_docx_text(act["transcript_path"])
        if not transcript_text.strip():
            conn.execute(
                "UPDATE activities SET status='error', error_msg=? WHERE id=?",
                ("Could not extract text from transcript.", act["id"])
            )
            conn.commit()
            return

        program_code = cand.get("program", "accelerate")
        activity_def = get_activity(program_code, activity_code)
        if not activity_def:
            conn.execute(
                "UPDATE activities SET status='error', error_msg=? WHERE id=?",
                ("Activity definition not found.", act["id"])
            )
            conn.commit()
            return

        kbi_defs = build_kbi_prompt(program_code, activity_code)
        program_name = PROGRAMS[program_code]["name"]

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=8096,
            messages=[{
                "role": "user",
                "content": ANALYSIS_PROMPT.format(
                    program_name=program_name,
                    activity_name=activity_def["name"],
                    candidate_role=activity_def["candidate_role"],
                    kbi_definitions=kbi_defs,
                    transcript_text=transcript_text[:40000],
                )
            }]
        )

        raw = message.content[0].text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        analysis = json.loads(raw)

        conn.execute(
            "UPDATE activities SET status='ready', analysis_json=?, analyzed_at=? WHERE id=?",
            (json.dumps(analysis), datetime.utcnow().isoformat(), act["id"])
        )
        conn.commit()

    except json.JSONDecodeError as e:
        conn.execute(
            "UPDATE activities SET status='error', error_msg=? WHERE id=?",
            (f"JSON parse error: {e}", act_row["id"] if act_row else "?")
        )
        conn.commit()
    except Exception as e:
        conn.execute(
            "UPDATE activities SET status='error', error_msg=? WHERE id=?",
            (str(e), act_row["id"] if act_row else "?")
        )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Routes — Pages
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    conn = get_db()
    candidates = conn.execute(
        "SELECT * FROM candidates ORDER BY created_at DESC"
    ).fetchall()
    enriched = []
    for c in candidates:
        cand = dict(c)
        acts = conn.execute(
            "SELECT activity_code, status FROM activities WHERE candidate_id=?",
            (c["id"],)
        ).fetchall()
        cand["act_statuses"] = {a["activity_code"]: a["status"] for a in acts}
        prog = PROGRAMS.get(cand.get("program", "accelerate"), {})
        cand["program_name"] = prog.get("name", "")
        cand["activity_codes"] = list(prog.get("activities", {}).keys())
        enriched.append(cand)
    conn.close()
    return templates.TemplateResponse("home.html", _ctx(request, candidates=enriched))


@app.post("/candidates/new")
async def new_candidate(
    request: Request,
    name: str = Form(...),
    position: str = Form(""),
    assessment_date: str = Form(""),
    assessors: str = Form(""),
    program: str = Form("accelerate"),
):
    cid = str(uuid.uuid4())
    conn = get_db()
    conn.execute(
        "INSERT INTO candidates (id, name, position, assessment_date, assessors, program, created_at) VALUES (?,?,?,?,?,?,?)",
        (cid, name.strip(), position.strip(), assessment_date, assessors.strip(), program, datetime.utcnow().isoformat())
    )
    # Pre-create activity rows for this program
    prog_acts = PROGRAMS.get(program, {}).get("activities", {})
    for act_code in prog_acts:
        act_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO activities (id, candidate_id, activity_code, status, created_at) VALUES (?,?,?,?,?)",
            (act_id, cid, act_code, "pending", datetime.utcnow().isoformat())
        )
    conn.commit()
    conn.close()
    return RedirectResponse(f"/candidates/{cid}", status_code=303)


@app.get("/candidates/{candidate_id}", response_class=HTMLResponse)
async def candidate_detail(request: Request, candidate_id: str):
    cand = get_candidate_with_activities(candidate_id)
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
    prog_code = cand.get("program", "accelerate")
    prog = PROGRAMS.get(prog_code, {})
    activity_defs = prog.get("activities", {})
    return templates.TemplateResponse("candidate.html", _ctx(
        request,
        cand=cand,
        activity_defs=activity_defs,
        prog_name=prog.get("name", ""),
    ))


@app.post("/candidates/{candidate_id}/activities/{activity_code}/upload")
async def upload_transcript(
    candidate_id: str,
    activity_code: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    conn = get_db()
    cand = conn.execute("SELECT * FROM candidates WHERE id=?", (candidate_id,)).fetchone()
    if not cand:
        conn.close()
        raise HTTPException(status_code=404, detail="Candidate not found")

    act = conn.execute(
        "SELECT * FROM activities WHERE candidate_id=? AND activity_code=?",
        (candidate_id, activity_code)
    ).fetchone()
    if not act:
        conn.close()
        raise HTTPException(status_code=404, detail="Activity not found")

    if not file.filename.lower().endswith(".docx"):
        conn.close()
        raise HTTPException(status_code=400, detail="Only .docx files are accepted")

    filename = f"{candidate_id}_{activity_code}_{file.filename}"
    save_path = UPLOAD_DIR / filename
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    conn.execute(
        "UPDATE activities SET transcript_filename=?, transcript_path=?, status='analyzing', error_msg=NULL WHERE id=?",
        (file.filename, str(save_path), act["id"])
    )
    conn.commit()
    conn.close()

    if not ANTHROPIC_API_KEY:
        conn2 = get_db()
        conn2.execute(
            "UPDATE activities SET status='error', error_msg=? WHERE id=?",
            ("ANTHROPIC_API_KEY is not set. Please add it in your Railway environment variables.", act["id"])
        )
        conn2.commit()
        conn2.close()
        return RedirectResponse(f"/candidates/{candidate_id}", status_code=303)

    background_tasks.add_task(run_analysis, candidate_id, activity_code)
    return RedirectResponse(f"/candidates/{candidate_id}", status_code=303)


@app.get("/candidates/{candidate_id}/activities/{activity_code}/status")
async def activity_status(candidate_id: str, activity_code: str):
    conn = get_db()
    act = conn.execute(
        "SELECT status, error_msg FROM activities WHERE candidate_id=? AND activity_code=?",
        (candidate_id, activity_code)
    ).fetchone()
    conn.close()
    if not act:
        return JSONResponse({"status": "not_found"})
    return JSONResponse({"status": act["status"], "error": act["error_msg"]})


@app.get("/candidates/{candidate_id}/activities/{activity_code}/verify", response_class=HTMLResponse)
async def verify_activity(request: Request, candidate_id: str, activity_code: str):
    cand = get_candidate_with_activities(candidate_id)
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
    act = cand["activities"].get(activity_code)
    if not act or act["status"] not in ("ready", "confirmed"):
        return RedirectResponse(f"/candidates/{candidate_id}", status_code=303)

    prog_code = cand.get("program", "accelerate")
    activity_def = get_activity(prog_code, activity_code)
    analysis = json.loads(act["analysis_json"]) if act.get("analysis_json") else {}
    confirmed = json.loads(act["confirmed_json"]) if act.get("confirmed_json") else {}

    # Merge confirmed overrides into analysis for display
    display_data = json.loads(act["analysis_json"]) if act.get("analysis_json") else {}
    if confirmed:
        for comp_code, comp_data in confirmed.get("competencies", {}).items():
            if comp_code in display_data.get("competencies", {}):
                display_data["competencies"][comp_code] = comp_data

    comp_order = get_comp_order(prog_code, activity_code)

    return templates.TemplateResponse("verify.html", _ctx(
        request,
        cand=cand,
        act=act,
        activity_code=activity_code,
        activity_def=activity_def,
        analysis=display_data,
        confirmed=confirmed,
        comp_order=comp_order,
        is_confirmed=act["status"] == "confirmed",
    ))


@app.post("/candidates/{candidate_id}/activities/{activity_code}/confirm")
async def confirm_ratings(request: Request, candidate_id: str, activity_code: str):
    body = await request.json()
    conn = get_db()
    act = conn.execute(
        "SELECT * FROM activities WHERE candidate_id=? AND activity_code=?",
        (candidate_id, activity_code)
    ).fetchone()
    if not act:
        conn.close()
        raise HTTPException(status_code=404)

    conn.execute(
        "UPDATE activities SET confirmed_json=?, status='confirmed', confirmed_at=? WHERE id=?",
        (json.dumps(body), datetime.utcnow().isoformat(), act["id"])
    )
    conn.commit()
    conn.close()
    return JSONResponse({"ok": True})


@app.get("/candidates/{candidate_id}/summary", response_class=HTMLResponse)
async def candidate_summary(request: Request, candidate_id: str):
    cand = get_candidate_with_activities(candidate_id)
    if not cand:
        raise HTTPException(status_code=404)

    prog_code = cand.get("program", "accelerate")
    prog = PROGRAMS.get(prog_code, {})
    activity_defs = prog.get("activities", {})

    # Build consolidated scores
    all_comp_scores: dict[str, list[int]] = {}
    activity_scores: dict[str, dict[str, int]] = {}

    for act_code, act in cand["activities"].items():
        if act["status"] != "confirmed":
            continue
        data = json.loads(act["confirmed_json"]) if act.get("confirmed_json") else {}
        act_scores = {}
        for comp_code, comp_data in data.get("competencies", {}).items():
            ov = comp_data.get("overall", 0)
            act_scores[comp_code] = ov
            all_comp_scores.setdefault(comp_code, []).append(ov)
        activity_scores[act_code] = act_scores

    consolidated = {c: max(scores) for c, scores in all_comp_scores.items()}

    # Pre-parse confirmed JSON for detail view
    activity_details: dict[str, dict] = {}
    for act_code, act in cand["activities"].items():
        if act.get("confirmed_json"):
            try:
                activity_details[act_code] = json.loads(act["confirmed_json"])
            except Exception:
                activity_details[act_code] = {}

    return templates.TemplateResponse("summary.html", _ctx(
        request,
        cand=cand,
        activity_defs=activity_defs,
        activity_scores=activity_scores,
        activity_details=activity_details,
        consolidated=consolidated,
        prog_name=prog.get("name", ""),
    ))


@app.get("/candidates/{candidate_id}/activities/{activity_code}/download")
async def download_rating_form(candidate_id: str, activity_code: str):
    """Download the filled-in rating form DOCX for a confirmed activity."""
    cand = get_candidate_with_activities(candidate_id)
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
    act = cand["activities"].get(activity_code)
    if not act or act["status"] != "confirmed":
        raise HTTPException(status_code=400, detail="Activity not confirmed yet")

    confirmed_data = json.loads(act["confirmed_json"]) if act.get("confirmed_json") else {}

    try:
        buf = generate_activity_document(activity_code, cand, confirmed_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document generation error: {e}")

    act_name = activity_code.upper().replace("CBI", "CBI_Interview_Guide").replace("AP", "AP_Rating_Form").replace(
        "GE", "GE_Rating_Form").replace("CR", "CR_Rating_Form").replace("NEG", "NEG_Rating_Form")
    safe_name = cand["name"].replace(" ", "_").replace(",", "").replace(".", "")
    date_str = (cand.get("assessment_date") or "").replace("-", "")
    filename = f"JG_DAC_{safe_name}_{date_str}_{act_name}.docx"

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/candidates/{candidate_id}/report/download")
async def download_report(candidate_id: str):
    """Download the consolidated DAC Report DOCX."""
    cand = get_candidate_with_activities(candidate_id)
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")

    prog_code = cand.get("program", "accelerate")

    # Gather all confirmed activity data
    all_confirmed: dict[str, dict] = {}
    all_comp_scores: dict[str, list[int]] = {}
    for act_code, act in cand["activities"].items():
        if act.get("status") == "confirmed" and act.get("confirmed_json"):
            try:
                data = json.loads(act["confirmed_json"])
                all_confirmed[act_code] = data
                for comp_code, comp_data in data.get("competencies", {}).items():
                    ov = comp_data.get("overall", 0)
                    if ov:
                        all_comp_scores.setdefault(comp_code, []).append(ov)
            except Exception:
                pass

    consolidated = {c: max(scores) for c, scores in all_comp_scores.items()}

    try:
        buf = generate_dac_report(cand, all_confirmed, consolidated)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {e}")

    safe_name = cand["name"].replace(" ", "_").replace(",", "").replace(".", "")
    date_str = (cand.get("assessment_date") or "").replace("-", "")
    filename = f"JG_DAC_Report_{safe_name}_{date_str}.docx"

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/candidates/{candidate_id}/delete")
async def delete_candidate(candidate_id: str):
    conn = get_db()
    conn.execute("DELETE FROM activities WHERE candidate_id=?", (candidate_id,))
    conn.execute("DELETE FROM candidates WHERE id=?", (candidate_id,))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)
