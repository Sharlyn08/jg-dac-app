# JG DAC Assessment Tool — Build Prompt for Google AI Studio

Paste everything below the horizontal line into Google AI Studio as your first message. Set the model to **Gemini 2.0 Flash** or **Gemini 1.5 Pro**.

---

## Your Task

Build a fully working **Jollibee Group Development Assessment Center (DAC) web application** using FastAPI, Jinja2, SQLite, and the **Google Gemini API**. The app helps assessors manage DAC candidates, upload activity transcripts, have AI analyze and rate behaviors, verify ratings, and download filled-in DOCX rating forms and a final DAC Report.

---

## Application Overview

**Tech stack:**
- Backend: FastAPI + Jinja2 templates + SQLite (via `sqlite3`) + BackgroundTasks
- AI: Google Gemini API (`google-generativeai` SDK), model `gemini-2.0-flash`
- DOCX generation: `python-docx`
- File upload: `python-multipart`
- Deployment: Railway (`railway.toml`)
- Frontend: Bootstrap 5.3 + Bootstrap Icons (CDN), custom CSS

**Programs supported:**
- **Accelerate**: 4 activities — Analysis Presentation (AP), Group Exercise (GE), Coaching Roleplay (CR), Competency-Based Interview (CBI)
- **First Loyalty**: 2 activities — Analysis Presentation (AP), Negotiation Role Play (NEG)

**5 Competencies (Inspire Joy Leadership Brands):**
- DSP = Drive Superior Performance
- WTP = Win Through People
- LFDV = Learn from Different Views
- MaD = Make a Difference
- ET = Establish Trust

**Rating scale:** 1 = Does Not Demonstrate, 2 = Inconsistently Demonstrates, 3 = Consistently Demonstrates, 4 = Exceeds Expectations

---

## File Structure to Generate

```
dac_app/
├── main.py                  ← FastAPI app (routes, DB, AI analysis)
├── kbi_data.py              ← KBI definitions for all activities
├── docx_generator.py        ← DOCX generation from templates
├── requirements.txt
├── railway.toml
├── .env.example
├── static/
│   └── style.css
├── templates/               ← Jinja2 HTML templates
│   ├── base.html
│   ├── home.html            ← Candidate list
│   ├── candidate.html       ← Activity cards + upload
│   ├── verify.html          ← AI rating review + confirm
│   └── summary.html         ← Consolidated scores + download buttons
└── templates_docx/          ← Blank DOCX templates (user provides these)
    ├── ap_rating_form.docx
    ├── ge_rating_form.docx
    ├── cr_rating_form.docx
    ├── cbi_guide.docx
    └── dac_report.docx
```

---

## Database Schema

```sql
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
```

**Activity status flow:** `pending` → `analyzing` → `ready` → `confirmed` (or `error`)

---

## main.py — Key Sections

### Environment / Config
```python
import os, uuid, json, sqlite3, io
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
from docx import Document

from kbi_data import PROGRAMS, COMP_META, LEVEL_LABELS, get_activity, build_kbi_prompt, get_comp_order
from docx_generator import generate_activity_document, generate_dac_report

DB_PATH = os.getenv("DB_PATH", "dac.db")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
```

### AI Analysis Function
```python
def run_analysis(candidate_id: str, activity_code: str):
    # 1. Load candidate + activity from DB
    # 2. Extract text from DOCX transcript using python-docx
    # 3. Build prompt using ANALYSIS_PROMPT template (see below)
    # 4. Call Gemini API:
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(
        prompt_text,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=8096,
            temperature=0.2,
        )
    )
    raw = response.text.strip()
    # 5. Strip markdown fences if present: if raw.startswith("```"): ...
    # 6. json.loads(raw) → save to DB as analysis_json, set status='ready'
```

### Analysis Prompt Template
```
You are an expert assessor for the Jollibee Group Development Assessment Center (DAC) {program_name} program.

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
{
  "competencies": {
    "COMP_CODE": {
      "kbis": [
        {
          "n": 1,
          "title": "KBI title",
          "suggested_rating": 2,
          "evidence": "Evidence and explanation"
        }
      ],
      "overall": 2,
      "rationale": "One-sentence rationale for the overall rating"
    }
  }
}
```

### Routes to implement
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Home — candidate list |
| POST | `/candidates/new` | Create candidate + pre-create activity rows |
| GET | `/candidates/{id}` | Candidate detail with activity cards |
| POST | `/candidates/{id}/activities/{code}/upload` | Save DOCX + trigger BackgroundTask analysis |
| GET | `/candidates/{id}/activities/{code}/status` | JSON status poll |
| GET | `/candidates/{id}/activities/{code}/verify` | Verify/edit AI ratings |
| POST | `/candidates/{id}/activities/{code}/confirm` | Save confirmed JSON |
| GET | `/candidates/{id}/summary` | Consolidated scores |
| GET | `/candidates/{id}/activities/{code}/download` | Download filled DOCX rating form |
| GET | `/candidates/{id}/report/download` | Download full DAC Report DOCX |
| POST | `/candidates/{id}/delete` | Delete candidate |

---

## kbi_data.py — Structure

```python
COMP_META = {
    "DSP": {"name": "Drive Superior Performance", "desc": "We are entrepreneurial; we collaborate across networks to realize the company's goals."},
    "MaD": {"name": "Make a Difference", "desc": "We take the lead and make a difference through continuous innovation that drives positive change."},
    "WTP": {"name": "Win Through People", "desc": "We earn commitment from our people. We hold each other accountable for performance with empathy and care."},
    "LFDV": {"name": "Learn from Different Views", "desc": "We constantly learn from different ideas to improve. We respect others enough to tell them what we think."},
    "ET": {"name": "Establish Trust", "desc": "We build the best team and trust them to make decisions and take calculated risks."},
}

LEVEL_LABELS = {1: "Does Not Demonstrate", 2: "Inconsistently Demonstrates", 3: "Consistently Demonstrates", 4: "Exceeds Expectations"}

PROGRAMS = {
    "accelerate": {
        "name": "Accelerate",
        "activities": {
            "ap": {
                "name": "Analysis Presentation", "short": "AP",
                "candidate_role": "Account Manager / Officer (presenting to senior management)",
                "competencies": {
                    "DSP": {"kbis": [
                        {"n": 1, "title": "Communicates clear recommendations and rationale", "dac": "Communicates clear recommendations and rationale aligned to business priorities"},
                        {"n": 2, "title": "Creates strategies and practical actions", "dac": "Develops strong strategies and practical actions to improve business performance"},
                        {"n": 3, "title": "Acts with the customer in mind", "dac": "Considers customer impact and commercial implications in decisions"},
                        {"n": 4, "title": "Anticipates risks and opportunities early", "dac": "Recognizes risks and opportunities early and recommends timely business action"},
                    ]},
                    "MaD": {"kbis": [
                        {"n": 1, "title": "Suggests practical improvements", "dac": "Suggests practical improvements to current business challenges"},
                        {"n": 2, "title": "Takes initiative despite incomplete information", "dac": "Takes initiative in addressing issues despite incomplete information"},
                        {"n": 3, "title": "Tests alternatives and adapts recommendations", "dac": "Tests alternatives, adapts recommendations, and incorporates broader perspectives"},
                    ]},
                    "ET": {"kbis": [
                        {"n": 1, "title": "Makes clear decisions and takes accountability", "dac": "Makes clear and timely decisions, takes accountability, and demonstrates ownership"},
                        {"n": 2, "title": "Balances stewardship and long-term impact", "dac": "Balances short-term decisions with long-term business impact and protection of company reputation"},
                        {"n": 3, "title": "Encourages cross-functional collaboration", "dac": "Encourages cross-functional collaboration and supports decisions using relevant data and expertise"},
                    ]},
                }
            },
            "ge": {
                "name": "Group Exercise", "short": "GE",
                "candidate_role": "Senior Manager (group strategic discussion with peers)",
                "competencies": {
                    "DSP": {"kbis": [
                        {"n": 1, "title": "Communicates compelling direction to energize the team", "dac": "Sets a clear direction and drives the group toward a high-quality strategic output"},
                        {"n": 2, "title": "Creates strategy and drives execution", "dac": "Develops strong strategies, structures the discussion, and pushes for concrete decisions"},
                        {"n": 3, "title": "Drives results-focused recommendations", "dac": "Grounds recommendations in data from the case and advocates for prioritized, actionable outcomes"},
                    ]},
                    "WTP": {"kbis": [
                        {"n": 1, "title": "Creates collaborative and inclusive discussion", "dac": "Ensures all voices are heard and creates a safe environment for contributions"},
                        {"n": 2, "title": "Inspires and motivates team toward shared outcome", "dac": "Rallies the group around a shared goal and maintains group energy and direction"},
                        {"n": 3, "title": "Provides structure and direction to the group", "dac": "Helps the group stay on track and monitors progress toward the activity goal"},
                    ]},
                    "LFDV": {"kbis": [
                        {"n": 1, "title": "Challenges assumptions and provokes better thinking", "dac": "Raises critical questions or reframes the problem to improve the quality of discussion"},
                        {"n": 2, "title": "Draws on diverse perspectives to improve decisions", "dac": "Synthesizes multiple viewpoints and uses data to strengthen group recommendations"},
                        {"n": 3, "title": "Adjusts position and incorporates better ideas", "dac": "Demonstrates openness to changing views when presented with better arguments or data"},
                    ]},
                }
            },
            "cr": {
                "name": "Coaching Roleplay", "short": "CR",
                "candidate_role": "Newly appointed COO / Senior Manager (coaching a direct report)",
                "competencies": {
                    "WTP": {"kbis": [
                        {"n": 1, "title": "Treats the coachee with empathy and care", "dac": "Listens first, acknowledges the coachee's perspective, and creates a safe space for the conversation"},
                        {"n": 2, "title": "Inspires and motivates toward high performance", "dac": "Acknowledges strengths and frames improvement as achievable; rebuilds confidence where needed"},
                        {"n": 3, "title": "Provides clear directions and expectations", "dac": "Sets specific, concrete expectations for performance improvement with agreed timelines"},
                        {"n": 4, "title": "Develops and coaches team members", "dac": "Uses a coaching approach (asking, not just telling) to build the coachee's own thinking and capability"},
                    ]},
                    "LFDV": {"kbis": [
                        {"n": 1, "title": "Listens to understand before acting", "dac": "Asks open-ended questions and listens actively before offering solutions or feedback"},
                        {"n": 2, "title": "Speaks up constructively regardless of pushback", "dac": "Maintains clear feedback and expectations even when the coachee challenges or deflects"},
                        {"n": 3, "title": "Adjusts approach based on what the coachee shares", "dac": "Adapts the coaching plan appropriately when given new information by the coachee"},
                    ]},
                    "ET": {"kbis": [
                        {"n": 1, "title": "Makes timely decisions and takes accountability", "dac": "Takes clear ownership of the situation and commits to specific follow-through"},
                        {"n": 2, "title": "Builds structure and empowers the coachee", "dac": "Creates a clear accountability framework (check-ins, milestones) that empowers the coachee to self-manage"},
                        {"n": 3, "title": "Acts with integrity and follows through", "dac": "Closes the session with clear mutual commitments and a shared understanding of next steps"},
                    ]},
                }
            },
            "cbi": {
                "name": "Competency-Based Interview", "short": "CBI",
                "candidate_role": "Officer / Manager (sharing real-world past experiences)",
                "competencies": {
                    "DSP": {"kbis": [
                        {"n": 1, "title": "Drives results with clear business impact", "dac": "Shares a story where specific actions led to measurable business outcomes"},
                        {"n": 2, "title": "Sets direction and leads execution", "dac": "Describes leading a project or initiative with clear direction, standards, and follow-through"},
                    ]},
                    "WTP": {"kbis": [
                        {"n": 1, "title": "Handles underperformance with empathy and accountability", "dac": "Shares a story of managing a difficult or underperforming team member with both care and clear consequences"},
                        {"n": 2, "title": "Coaches and develops others", "dac": "Describes a specific instance of developing someone's skills or capability through coaching or mentoring"},
                        {"n": 3, "title": "Maintains team commitment under pressure", "dac": "Shares how they kept a team motivated and aligned during a difficult or high-pressure situation"},
                    ]},
                    "LFDV": {"kbis": [
                        {"n": 1, "title": "Proactively seeks and acts on feedback", "dac": "Shares a specific instance of asking for and meaningfully incorporating feedback from others"},
                        {"n": 2, "title": "Resolves disagreement through data and diverse input", "dac": "Describes navigating a conflict of views using evidence or by bringing in different perspectives"},
                        {"n": 3, "title": "Adjusts position when presented with better evidence", "dac": "Shares a time when they changed their stance based on a better idea or new information"},
                    ]},
                    "MaD": {"kbis": [
                        {"n": 1, "title": "Drives innovation or change despite resistance", "dac": "Shares a story of championing a new idea or process change and overcoming initial pushback"},
                        {"n": 2, "title": "Encourages others to try new approaches", "dac": "Describes how they created space for experimentation or learning in their team or organization"},
                    ]},
                    "ET": {"kbis": [
                        {"n": 1, "title": "Makes difficult decisions and owns the outcome", "dac": "Shares a situation requiring a hard judgment call and describes taking full accountability for the result"},
                        {"n": 2, "title": "Empowers others and builds accountability", "dac": "Describes delegating meaningfully to a team member and creating a follow-through structure"},
                    ]},
                }
            },
        }
    },
    "first_loyalty": {
        "name": "First Loyalty",
        "activities": {
            "ap": {
                "name": "Analysis Presentation", "short": "AP",
                "candidate_role": "Account Manager (presenting to senior management)",
                "competencies": {
                    "DSP": {"kbis": [
                        {"n": 1, "title": "Communicates clear recommendations and rationale", "dac": "Communicates clear recommendations and rationale aligned to business priorities"},
                        {"n": 2, "title": "Creates breakthrough strategies and practical actions", "dac": "Develops strong strategies and practical actions to improve business performance"},
                        {"n": 3, "title": "Acts with the customer in mind", "dac": "Considers customer impact and commercial implications in decisions"},
                        {"n": 4, "title": "Anticipates risks and opportunities early", "dac": "Recognizes risks and opportunities early and recommends timely business action"},
                    ]},
                    "MaD": {"kbis": [
                        {"n": 1, "title": "Drives change with practical improvements", "dac": "Suggests practical improvements to current business challenges"},
                        {"n": 2, "title": "Takes initiative despite incomplete information", "dac": "Takes initiative in addressing issues despite incomplete information"},
                        {"n": 3, "title": "Tests alternatives and adapts", "dac": "Tests alternatives, adapts recommendations, and incorporates broader perspectives"},
                    ]},
                    "ET": {"kbis": [
                        {"n": 1, "title": "Makes clear and timely decisions", "dac": "Makes clear and timely decisions, takes accountability, and demonstrates ownership"},
                        {"n": 2, "title": "Balances short-term and long-term stewardship", "dac": "Balances short-term decisions with long-term business impact and protection of company reputation"},
                        {"n": 3, "title": "Encourages cross-functional collaboration", "dac": "Encourages cross-functional collaboration and supports decisions using relevant data and expertise"},
                    ]},
                }
            },
            "neg": {
                "name": "Negotiation Role Play", "short": "NEG",
                "candidate_role": "Account Manager (managing a client escalation / negotiation)",
                "competencies": {
                    "DSP": {"kbis": [
                        {"n": 1, "title": "Identifies the most important issue and prioritizes action", "dac": "Identifies the most important issue and prioritizes action to protect the client relationship"},
                        {"n": 2, "title": "Provides practical, well-structured solutions", "dac": "Provides practical, well-structured solutions with clear rationale"},
                        {"n": 3, "title": "Balances customer needs and company interests", "dac": "Balances customer needs, commercial impact, and company interests in decisions"},
                        {"n": 4, "title": "Recognizes opportunities to strengthen partnership", "dac": "Recognizes opportunities to strengthen the long-term partnership beyond issue resolution"},
                    ]},
                    "WTP": {"kbis": [
                        {"n": 1, "title": "Builds rapport and manages with empathy", "dac": "Builds rapport and manages the conversation with empathy, professionalism, and respect"},
                        {"n": 2, "title": "Rebuilds confidence and secures commitment", "dac": "Rebuilds confidence and gains commitment toward sustained partnership and next steps"},
                        {"n": 3, "title": "Sets clear expectations and addresses accountability", "dac": "Sets clear expectations and addresses performance concerns through defined accountability"},
                        {"n": 4, "title": "Builds shared ownership and buy-in", "dac": "Builds client buy-in by creating shared ownership and commitment to agreed actions"},
                    ]},
                    "LFDV": {"kbis": [
                        {"n": 1, "title": "Asks thoughtful questions and listens actively", "dac": "Asks thoughtful questions and listens actively to understand the client's concerns"},
                        {"n": 2, "title": "Shares views and provides constructive challenge", "dac": "Shares views clearly and provides constructive challenge while maintaining openness"},
                        {"n": 3, "title": "Draws on client's perspective to improve decisions", "dac": "Draws on the client's perspective and uses it to improve decisions and next steps"},
                    ]},
                    "ET": {"kbis": [
                        {"n": 1, "title": "Takes clear ownership and follows through", "dac": "Takes clear ownership of issues and follows through on commitments"},
                        {"n": 2, "title": "Balances recovery with long-term stewardship", "dac": "Balances immediate client recovery with long-term business impact and protection of company reputation"},
                        {"n": 3, "title": "Enables confident, well-informed decisions", "dac": "Enables confident, well-informed decisions by establishing clear ownership and accountability"},
                    ]},
                }
            },
        }
    }
}

def get_activity(program_code: str, activity_code: str) -> dict | None:
    prog = PROGRAMS.get(program_code)
    if not prog: return None
    return prog["activities"].get(activity_code)

def build_kbi_prompt(program_code: str, activity_code: str) -> str:
    activity = get_activity(program_code, activity_code)
    if not activity: return ""
    lines = []
    for comp_code, comp_data in activity["competencies"].items():
        comp_name = COMP_META[comp_code]["name"]
        lines.append(f"\n## {comp_code} — {comp_name}")
        for kbi in comp_data["kbis"]:
            lines.append(f"  KBI {kbi['n']}: {kbi['title']}")
            lines.append(f"  DAC context: {kbi['dac']}")
    return "\n".join(lines)

def get_comp_order(program_code: str, activity_code: str) -> list[str]:
    activity = get_activity(program_code, activity_code)
    if not activity: return []
    return list(activity["competencies"].keys())
```

---

## docx_generator.py — Key Logic

The DOCX generator modifies template files using `python-docx`. The template DOCX files live in `templates_docx/` and were created from real JG DAC sample rating forms.

**Rating form structure (per competency table, 4-column):**
- Row 0: `[COMP NAME (black bg)] | [IJ Demonstration: X]` — update rating number here
- Row 1: Competency definition (merged, unchanged)
- Per KBI block (5 rows each, starting row 2):
  - Row+0: KBI title (black bg, all cols merged)
  - Row+1: `LEVEL 1 | LEVEL 2 | LEVEL 3 | LEVEL 4` (gray bg headers)
  - Row+2: Level descriptors — set `fill=FFFF00` on the selected level column, `FFFFFF` on others
  - Row+3: Key Progression (leave as-is)
  - Row+4: Evidence cell (merged) — replace with AI evidence text

**Key helper functions:**
```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_cell_fill(cell, fill_hex: str):
    tc = cell._tc
    tcPr = tc.find(qn("w:tcPr"))
    if tcPr is None:
        tcPr = OxmlElement("w:tcPr"); tc.insert(0, tcPr)
    shd = tcPr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd"); tcPr.append(shd)
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill_hex)

def get_unique_cells(row):
    seen, out = set(), []
    for cell in row.cells:
        cid = id(cell._tc)
        if cid not in seen:
            seen.add(cid); out.append(cell)
    return out
```

**Name replacement in text boxes / footers** (the candidate name appears in embedded XML):
```python
import zipfile, io

def replace_text_in_docx(buf: io.BytesIO, old: str, new: str) -> io.BytesIO:
    buf.seek(0)
    out = io.BytesIO()
    with zipfile.ZipFile(buf, "r") as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith(".xml") or item.filename.endswith(".rels"):
                text = data.decode("utf-8", errors="replace")
                if old in text:
                    text = text.replace(old, new)
                    data = text.encode("utf-8")
            zout.writestr(item, data)
    out.seek(0)
    return out
```

---

## requirements.txt

```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
jinja2>=3.1.4
python-multipart>=0.0.9
google-generativeai>=0.7.0
python-docx>=1.1.2
aiofiles>=23.2.1
```

---

## railway.toml

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

---

## .env.example

```
GOOGLE_API_KEY=AIza...
DB_PATH=dac.db
UPLOAD_DIR=uploads
```

---

## UI Behavior Notes

**Home page (`/`):**
- Lists all candidates as cards with activity status badges
- "New Candidate" button opens a modal (name, position, date, assessors, program selector)
- Activity badges: pending=gray, analyzing=yellow+spinner, ready=orange, confirmed=green, error=red

**Candidate detail (`/candidates/{id}`):**
- One card per activity
- Pending: shows "Upload transcript (.docx)" button (file input, auto-submits on select)
- Analyzing: shows spinner + polling JS (fetches `/status` every 4 seconds, reloads on state change)
- Ready: shows "Verify AI ratings" button
- Confirmed: shows "Edit ratings" + "Download form" buttons

**Verify page (`/candidates/{id}/activities/{code}/verify`):**
- Renders all competencies and KBIs dynamically from injected JSON via JavaScript
- Rating buttons (1–2–3–4) with color coding: 1=red, 2=orange, 3=green, 4=dark green
- Editable evidence textareas pre-filled with AI evidence
- "Confirm ratings" sends JSON POST to `/confirm` endpoint

**Summary page (`/candidates/{id}/summary`):**
- Color-coded score table (per activity × competency)
- Consolidated score = max across activities
- "Download DAC Report" button (top right)
- Per-activity detail section with KBI-level evidence

---

## Important Implementation Notes

1. **Background task**: Use FastAPI's `BackgroundTasks` for AI analysis so the upload returns immediately. Set status to `analyzing` before adding the task.

2. **Transcript truncation**: Truncate transcript text to 40,000 characters before sending to Gemini to stay within token limits.

3. **JSON parsing**: Strip markdown code fences from Gemini's response before `json.loads()`:
   ```python
   if raw.startswith("```"):
       raw = raw.split("```")[1]
       if raw.startswith("json"):
           raw = raw[4:]
   ```

4. **No API key handling**: If `GOOGLE_API_KEY` is not set, set activity status to `error` with a clear message.

5. **Jinja2 globals**: Register these in `templates.env.globals` and `templates.env.filters`:
   ```python
   templates.env.globals["PROGRAMS"] = PROGRAMS
   templates.env.globals["COMP_META"] = COMP_META
   templates.env.globals["LEVEL_LABELS"] = LEVEL_LABELS
   templates.env.globals["activity_status_label"] = activity_status_label
   templates.env.filters["fromjson"] = json.loads
   ```

6. **Scoring table color fills** (DAC Report summary): For rating R, the middle row of each 3-row competency block uses `262A2D` (dark) for levels ≤ R and the standard bar color for levels > R: L2=`FFC000`, L3=`92D050`, L4=`00B050`.

7. **DOCX templates**: The app needs the actual `.docx` template files in `templates_docx/`. These are rating forms specific to the JG DAC program — the user will provide them. The generator modifies them in-memory (not on disk) and streams them as a download.

---

Now generate all the files for this application. Start with `main.py`, then `kbi_data.py`, `docx_generator.py`, the HTML templates, and the config files. Make the code complete and production-ready.
