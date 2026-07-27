"""
KBI definitions for JG DAC Accelerate program.
Sourced directly from the 2026 official forms:
  - JG_DAC A&H Analysis Rating Form (AP)
  - JG_DAC Banco Group Exercise Rating Form (GE)
  - JG_DAC Right to Wear Coaching Rating Form (CR)
  - JFC_DAC Leadership Brand Interview Guide Form (CBI)

Competency matrix (which activities assess which competencies):
  AP  → Drive Superior Performance, Make a Difference, Establish Trust
  GE  → Win Through People, Learn from Different Views, Make a Difference
  CR  → Drive Superior Performance, Win Through People, Learn from Different Views, Establish Trust
  CBI → All 5 competencies
"""

COMP_META = {
    "DSP": {
        "name": "Drive Superior Performance",
        "desc": (
            "We are entrepreneurial; we believe in Jollibee Group's vision. "
            "We collaborate across our internal, functional, and local networks "
            "to realize the company's goals and vision."
        ),
    },
    "WTP": {
        "name": "Win Through People",
        "desc": (
            "We earn commitment from our people. We hold each other accountable "
            "for performance with empathy and care. We build a culture of family, "
            "joy, and inclusion."
        ),
    },
    "LFDV": {
        "name": "Learn from Different Views",
        "desc": (
            "We constantly learn from the different ideas of people to further improve. "
            "We respect others enough to tell them what we think. We proactively "
            "seek and share feedback."
        ),
    },
    "MaD": {
        "name": "Make a Difference",
        "desc": (
            "We take the lead and make a difference through continuous innovation "
            "that drives positive change for the Jollibee Group. We value progress "
            "over perfection."
        ),
    },
    "ET": {
        "name": "Establish Trust",
        "desc": (
            "We are aligned around our global perspective. We build the best team "
            "and trust them to make decisions and take calculated risks so we can "
            "make a positive impact."
        ),
    },
}

LEVEL_LABELS = {
    1: "Does Not Demonstrate",
    2: "Inconsistently Demonstrates",
    3: "Consistently Demonstrates",
    4: "Exceeds Expectations",
}

PROGRAMS = {
    "accelerate": {
        "name": "Accelerate",
        "activities": {
            # ──────────────────────────────────────────────────────────────
            # ANALYSIS PRESENTATION — DSP, MaD, ET
            # ──────────────────────────────────────────────────────────────
            "ap": {
                "name": "Analysis Presentation",
                "short": "AP",
                "candidate_role": (
                    "Officer presenting strategic analysis and recommendations "
                    "to senior management (A&H Tissue fictional case)"
                ),
                "competencies": {
                    "DSP": {
                        "kbis": [
                            {
                                "n": 1,
                                "title": "Communicates a compelling and inspiring vision or purpose to energize the team",
                                "dac": "Communicates clear recommendations and rationale aligned to business priorities",
                            },
                            {
                                "n": 2,
                                "title": "Creates breakthrough strategies and stretched goals, and collaborates effectively to execute them with excellence",
                                "dac": "Develops strong strategies and practical actions to improve business performance",
                            },
                            {
                                "n": 3,
                                "title": "Acts with the customer in mind; delights our customers with exceptional products and services",
                                "dac": "Considers customer impact and commercial implications in decisions",
                            },
                            {
                                "n": 4,
                                "title": "Anticipates, sees ahead, seeks, and rapidly acts on opportunities to elevate the business",
                                "dac": "Recognizes risks and opportunities early and recommends timely business action",
                            },
                        ]
                    },
                    "MaD": {
                        "kbis": [
                            {
                                "n": 1,
                                "title": "Drives change and leads with courage; perseveres despite ambiguity",
                                "dac": "Suggests practical improvements to current business challenges",
                            },
                            {
                                "n": 2,
                                "title": "Champions experimentation and encourages tenacity in learning and improving",
                                "dac": "Takes initiative in addressing issues despite incomplete information",
                            },
                            {
                                "n": 3,
                                "title": "Remains curious and open to new ideas and experiences and considers issues from a multi-cultural or geographic (regional/global) perspective",
                                "dac": "Tests alternatives, adapts recommendations, and incorporates broader perspectives to improve outcomes",
                            },
                        ]
                    },
                    "ET": {
                        "kbis": [
                            {
                                "n": 1,
                                "title": "Makes timely decisions to resolve issues or problems and takes full responsibility for them, regardless of the outcome",
                                "dac": "Makes clear and timely decisions, takes accountability for recommendations, and demonstrates ownership of outcomes",
                            },
                            {
                                "n": 2,
                                "title": "Promotes and drives good stewardship of the company's resources and reputation",
                                "dac": "Balances short-term decisions with long-term business impact, responsible use of resources, and protection of company reputation",
                            },
                            {
                                "n": 3,
                                "title": "Builds the best team and empowers them to make decisions based on data and expertise",
                                "dac": "Encourages cross-functional collaboration and supports decisions using relevant data and operational expertise",
                            },
                        ]
                    },
                },
            },

            # ──────────────────────────────────────────────────────────────
            # GROUP EXERCISE — WTP, LFDV, MaD
            # ──────────────────────────────────────────────────────────────
            "ge": {
                "name": "Group Exercise",
                "short": "GE",
                "candidate_role": (
                    "Officer participating in a group strategic discussion "
                    "with peers (Banco fictional case)"
                ),
                "competencies": {
                    "WTP": {
                        "kbis": [
                            {
                                "n": 1,
                                "title": "Treats people with empathy and care and creates an enjoyable workplace",
                                "dac": "Builds rapport and creates a respectful, collaborative discussion environment",
                            },
                            {
                                "n": 2,
                                "title": "Inspires and motivates individuals and teams to high performance",
                                "dac": "Builds alignment and commitment toward shared decisions",
                            },
                            {
                                "n": 3,
                                "title": "Provides people with clear directions, standards of performance, and expectations and acts decisively to address poor performance",
                                "dac": "Helps the group stay focused on priorities and move toward decisions",
                            },
                            {
                                "n": 4,
                                "title": "Commits to people development and career growth; provides coaching and mentoring",
                                "dac": "Supports collaboration by enabling others to contribute effectively to group outcomes",
                            },
                        ]
                    },
                    "LFDV": {
                        "kbis": [
                            {
                                "n": 1,
                                "title": "Proactively gives and seeks feedback to learn from each other. Listens to understand",
                                "dac": "Asks thoughtful questions and listens actively to understand different viewpoints",
                            },
                            {
                                "n": 2,
                                "title": "Speaks up to share his/her point of view or provide constructive feedback regardless of audience",
                                "dac": "Shares ideas clearly and provides constructive challenge during discussion",
                            },
                            {
                                "n": 3,
                                "title": "Draws on the diverse backgrounds, skills and knowledge of people and ensures that everyone can contribute",
                                "dac": "Encourages contribution from others and builds on diverse perspectives",
                            },
                        ]
                    },
                    "MaD": {
                        "kbis": [
                            {
                                "n": 1,
                                "title": "Drives change and leads with courage; perseveres despite ambiguity",
                                "dac": "Proactively suggests practical improvements and drives the discussion forward despite ambiguity",
                            },
                            {
                                "n": 2,
                                "title": "Champions experimentation and encourages tenacity in learning and improving",
                                "dac": "Explores alternative approaches and supports trying better solutions",
                            },
                            {
                                "n": 3,
                                "title": "Remains curious and open to new ideas and experiences and considers issues from a multi-cultural or geographic perspective",
                                "dac": "Brings broader market, customer, or regional perspectives into the discussion",
                            },
                        ]
                    },
                },
            },

            # ──────────────────────────────────────────────────────────────
            # COACHING ROLEPLAY — DSP, WTP, LFDV, ET
            # ──────────────────────────────────────────────────────────────
            "cr": {
                "name": "Coaching Roleplay",
                "short": "CR",
                "candidate_role": (
                    "Officer conducting a coaching conversation with a direct report "
                    "(Right to Wear fictional case)"
                ),
                "competencies": {
                    "DSP": {
                        "kbis": [
                            {
                                "n": 1,
                                "title": "Communicates a compelling and inspiring vision or purpose to energize the team",
                                "dac": "Sets clear performance expectations and standards",
                            },
                            {
                                "n": 2,
                                "title": "Creates breakthrough strategies and stretched goals, and collaborates effectively to execute them with excellence",
                                "dac": "Encourages accountability for performance outcomes and improvement actions",
                            },
                            {
                                "n": 3,
                                "title": "Acts with the customer in mind; delights our customers with exceptional products and services",
                                "dac": "Drives clear actions and follow-through for performance improvement aligned to customer impact",
                            },
                            {
                                "n": 4,
                                "title": "Anticipates, sees ahead, seeks, and rapidly acts on opportunities to elevate the business",
                                "dac": "Identifies root causes and takes timely action to improve results",
                            },
                        ]
                    },
                    "WTP": {
                        "kbis": [
                            {
                                "n": 1,
                                "title": "Treats people with empathy and care and creates an enjoyable workplace",
                                "dac": "Builds rapport and creates a supportive coaching environment",
                            },
                            {
                                "n": 2,
                                "title": "Inspires and motivates individuals and teams to high performance",
                                "dac": "Encourages the employee to take accountability for performance improvement",
                            },
                            {
                                "n": 3,
                                "title": "Provides people with clear directions, standards of performance, and expectations and acts decisively to address poor performance",
                                "dac": "Provides clear, direct and constructive feedback and addresses performance gaps",
                            },
                            {
                                "n": 4,
                                "title": "Commits to people development and career growth; provides coaching and mentoring",
                                "dac": "Supports development through coaching, guidance, and practical next steps",
                            },
                        ]
                    },
                    "LFDV": {
                        "kbis": [
                            {
                                "n": 1,
                                "title": "Proactively gives and seeks feedback to learn from each other. Listens to understand",
                                "dac": "Asks thoughtful questions to understand performance issues and root causes",
                            },
                            {
                                "n": 2,
                                "title": "Speaks up to share his/her point of view or provide constructive feedback regardless of audience",
                                "dac": "Provides constructive feedback while remaining open to dialogue",
                            },
                            {
                                "n": 3,
                                "title": "Draws on the diverse backgrounds, skills and knowledge of people and ensures that everyone can contribute",
                                "dac": "Listens openly and responds with understanding to different perspectives",
                            },
                        ]
                    },
                    "ET": {
                        "kbis": [
                            {
                                "n": 1,
                                "title": "Makes timely decisions to resolve issues or problems and takes full responsibility for them, regardless of the outcome",
                                "dac": "Takes personal ownership of decisions and follows through on commitments",
                            },
                            {
                                "n": 2,
                                "title": "Promotes and drives good stewardship of the company's resources and reputation",
                                "dac": "Balances short-term decisions with long-term business impact, responsible use of resources, and protection of company reputation",
                            },
                            {
                                "n": 3,
                                "title": "Builds the best team and empowers them to make decisions based on data and expertise",
                                "dac": "Addresses performance concerns clearly and empowers others to take ownership and make decisions based on available data and information",
                            },
                        ]
                    },
                },
            },

            # ──────────────────────────────────────────────────────────────
            # COMPETENCY-BASED INTERVIEW — All 5 competencies
            # ──────────────────────────────────────────────────────────────
            "cbi": {
                "name": "Competency-Based Interview",
                "short": "CBI",
                "candidate_role": (
                    "Officer sharing real past behavioral examples using the "
                    "SBII (Situation-Behavior-Impact-Intent) format for all 5 "
                    "Leadership Brands"
                ),
                "competencies": {
                    "DSP": {
                        "kbis": [
                            {
                                "n": 1,
                                "title": "Communicates a compelling and inspiring vision or purpose to energize the team",
                                "dac": "Communicates clear recommendations and rationale aligned to business priorities",
                            },
                            {
                                "n": 2,
                                "title": "Creates breakthrough strategies and stretched goals, and collaborates effectively to execute them with excellence",
                                "dac": "Develops strong strategies and practical actions to improve business performance",
                            },
                            {
                                "n": 3,
                                "title": "Acts with the customer in mind; delights our customers with exceptional products and services",
                                "dac": "Considers customer impact and commercial implications in decisions",
                            },
                            {
                                "n": 4,
                                "title": "Anticipates, sees ahead, seeks, and rapidly acts on opportunities to elevate the business",
                                "dac": "Recognizes risks and opportunities early and acts on them",
                            },
                        ]
                    },
                    "WTP": {
                        "kbis": [
                            {
                                "n": 1,
                                "title": "Treats people with empathy and care and creates an enjoyable workplace",
                                "dac": "Builds rapport and creates a supportive environment for difficult conversations",
                            },
                            {
                                "n": 2,
                                "title": "Inspires and motivates individuals and teams to high performance",
                                "dac": "Inspires and motivates individuals or teams toward a shared goal",
                            },
                            {
                                "n": 3,
                                "title": "Provides people with clear directions, standards of performance, and expectations and acts decisively to address poor performance",
                                "dac": "Provides clear expectations and acts decisively on underperformance",
                            },
                            {
                                "n": 4,
                                "title": "Commits to people development and career growth; provides coaching and mentoring",
                                "dac": "Coaches and develops team members to grow capability",
                            },
                        ]
                    },
                    "LFDV": {
                        "kbis": [
                            {
                                "n": 1,
                                "title": "Proactively gives and seeks feedback to learn from each other. Listens to understand",
                                "dac": "Proactively seeks and acts on feedback; listens to understand different viewpoints",
                            },
                            {
                                "n": 2,
                                "title": "Speaks up to share his/her point of view or provide constructive feedback regardless of audience",
                                "dac": "Speaks up confidently and provides constructive challenge regardless of audience",
                            },
                            {
                                "n": 3,
                                "title": "Draws on the diverse backgrounds, skills and knowledge of people and ensures that everyone can contribute",
                                "dac": "Draws on diverse perspectives and ensures everyone can contribute",
                            },
                        ]
                    },
                    "MaD": {
                        "kbis": [
                            {
                                "n": 1,
                                "title": "Drives change and leads with courage; perseveres despite ambiguity",
                                "dac": "Drives change and leads with courage despite resistance or ambiguity",
                            },
                            {
                                "n": 2,
                                "title": "Champions experimentation and encourages tenacity in learning and improving",
                                "dac": "Champions experimentation and encourages others to try new approaches",
                            },
                            {
                                "n": 3,
                                "title": "Remains curious and open to new ideas and experiences and considers issues from a multi-cultural or geographic (regional/global) perspective",
                                "dac": "Remains curious and considers issues from multiple cultural or geographic perspectives",
                            },
                        ]
                    },
                    "ET": {
                        "kbis": [
                            {
                                "n": 1,
                                "title": "Makes timely decisions to resolve issues or problems and takes full responsibility for them, regardless of the outcome",
                                "dac": "Makes difficult or timely decisions and takes full accountability for outcomes",
                            },
                            {
                                "n": 2,
                                "title": "Promotes and drives good stewardship of the company's resources and reputation",
                                "dac": "Promotes responsible stewardship of company resources and reputation",
                            },
                            {
                                "n": 3,
                                "title": "Builds the best team and empowers them to make decisions based on data and expertise",
                                "dac": "Builds team capability and empowers others to make data-driven decisions",
                            },
                        ]
                    },
                },
            },
        },
    },
}


def get_activity(program_code: str, activity_code: str) -> dict | None:
    prog = PROGRAMS.get(program_code)
    if not prog:
        return None
    return prog["activities"].get(activity_code)


def build_kbi_prompt(program_code: str, activity_code: str) -> str:
    """Build a structured KBI reference string for the AI analysis prompt."""
    activity = get_activity(program_code, activity_code)
    if not activity:
        return ""
    lines = []
    for comp_code, comp_data in activity["competencies"].items():
        comp_name = COMP_META[comp_code]["name"]
        comp_desc = COMP_META[comp_code]["desc"]
        lines.append(f"\n## {comp_code} — {comp_name}")
        lines.append(f"Definition: {comp_desc}")
        for kbi in comp_data["kbis"]:
            lines.append(f"\n  KBI {kbi['n']}: {kbi['title']}")
            lines.append(f"  DAC equivalent behavior: {kbi['dac']}")
    return "\n".join(lines)


def get_comp_order(program_code: str, activity_code: str) -> list[str]:
    """Return competency codes in display order for a given activity."""
    activity = get_activity(program_code, activity_code)
    if not activity:
        return []
    return list(activity["competencies"].keys())
