"""
KBI definitions for JG DAC programs.
Each activity lists which competencies it measures and the KBIs under each.
"""

COMP_META = {
    "DSP": {"name": "Drive Superior Performance", "desc": "We are entrepreneurial; we collaborate across networks to realize the company's goals."},
    "MaD": {"name": "Make a Difference", "desc": "We take the lead and make a difference through continuous innovation that drives positive change."},
    "WTP": {"name": "Win Through People", "desc": "We earn commitment from our people. We hold each other accountable for performance with empathy and care."},
    "LFDV": {"name": "Learn from Different Views", "desc": "We constantly learn from different ideas to improve. We respect others enough to tell them what we think."},
    "ET": {"name": "Establish Trust", "desc": "We build the best team and trust them to make decisions and take calculated risks."},
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
            "ap": {
                "name": "Analysis Presentation",
                "short": "AP",
                "candidate_role": "Account Manager / Officer (presenting to senior management)",
                "competencies": {
                    "DSP": {
                        "kbis": [
                            {"n": 1, "title": "Communicates clear recommendations and rationale", "dac": "Communicates clear recommendations and rationale aligned to business priorities"},
                            {"n": 2, "title": "Creates strategies and practical actions", "dac": "Develops strong strategies and practical actions to improve business performance"},
                            {"n": 3, "title": "Acts with the customer in mind", "dac": "Considers customer impact and commercial implications in decisions"},
                            {"n": 4, "title": "Anticipates risks and opportunities early", "dac": "Recognizes risks and opportunities early and recommends timely business action"},
                        ]
                    },
                    "MaD": {
                        "kbis": [
                            {"n": 1, "title": "Suggests practical improvements", "dac": "Suggests practical improvements to current business challenges"},
                            {"n": 2, "title": "Takes initiative despite incomplete information", "dac": "Takes initiative in addressing issues despite incomplete information"},
                            {"n": 3, "title": "Tests alternatives and adapts recommendations", "dac": "Tests alternatives, adapts recommendations, and incorporates broader perspectives"},
                        ]
                    },
                    "ET": {
                        "kbis": [
                            {"n": 1, "title": "Makes clear decisions and takes accountability", "dac": "Makes clear and timely decisions, takes accountability, and demonstrates ownership"},
                            {"n": 2, "title": "Balances stewardship and long-term impact", "dac": "Balances short-term decisions with long-term business impact and protection of company reputation"},
                            {"n": 3, "title": "Encourages cross-functional collaboration", "dac": "Encourages cross-functional collaboration and supports decisions using relevant data and expertise"},
                        ]
                    },
                },
            },
            "ge": {
                "name": "Group Exercise",
                "short": "GE",
                "candidate_role": "Senior Manager (group strategic discussion with peers)",
                "competencies": {
                    "DSP": {
                        "kbis": [
                            {"n": 1, "title": "Communicates compelling direction to energize the team", "dac": "Sets a clear direction and drives the group toward a high-quality strategic output"},
                            {"n": 2, "title": "Creates strategy and drives execution", "dac": "Develops strong strategies, structures the discussion, and pushes for concrete decisions"},
                            {"n": 3, "title": "Drives results-focused recommendations", "dac": "Grounds recommendations in data from the case and advocates for prioritized, actionable outcomes"},
                        ]
                    },
                    "WTP": {
                        "kbis": [
                            {"n": 1, "title": "Creates collaborative and inclusive discussion", "dac": "Ensures all voices are heard and creates a safe environment for contributions"},
                            {"n": 2, "title": "Inspires and motivates team toward shared outcome", "dac": "Rallies the group around a shared goal and maintains group energy and direction"},
                            {"n": 3, "title": "Provides structure and direction to the group", "dac": "Helps the group stay on track and monitors progress toward the activity goal"},
                        ]
                    },
                    "LFDV": {
                        "kbis": [
                            {"n": 1, "title": "Challenges assumptions and provokes better thinking", "dac": "Raises critical questions or reframes the problem to improve the quality of discussion"},
                            {"n": 2, "title": "Draws on diverse perspectives to improve decisions", "dac": "Synthesizes multiple viewpoints and uses data to strengthen group recommendations"},
                            {"n": 3, "title": "Adjusts position and incorporates better ideas", "dac": "Demonstrates openness to changing views when presented with better arguments or data"},
                        ]
                    },
                },
            },
            "cr": {
                "name": "Coaching Roleplay",
                "short": "CR",
                "candidate_role": "Newly appointed COO / Senior Manager (coaching a direct report)",
                "competencies": {
                    "WTP": {
                        "kbis": [
                            {"n": 1, "title": "Treats the coachee with empathy and care", "dac": "Listens first, acknowledges the coachee's perspective, and creates a safe space for the conversation"},
                            {"n": 2, "title": "Inspires and motivates toward high performance", "dac": "Acknowledges strengths and frames improvement as achievable; rebuilds confidence where needed"},
                            {"n": 3, "title": "Provides clear directions and expectations", "dac": "Sets specific, concrete expectations for performance improvement with agreed timelines"},
                            {"n": 4, "title": "Develops and coaches team members", "dac": "Uses a coaching approach (asking, not just telling) to build the coachee's own thinking and capability"},
                        ]
                    },
                    "LFDV": {
                        "kbis": [
                            {"n": 1, "title": "Listens to understand before acting", "dac": "Asks open-ended questions and listens actively before offering solutions or feedback"},
                            {"n": 2, "title": "Speaks up constructively regardless of pushback", "dac": "Maintains clear feedback and expectations even when the coachee challenges or deflects"},
                            {"n": 3, "title": "Adjusts approach based on what the coachee shares", "dac": "Adapts the coaching plan appropriately when given new information by the coachee"},
                        ]
                    },
                    "ET": {
                        "kbis": [
                            {"n": 1, "title": "Makes timely decisions and takes accountability", "dac": "Takes clear ownership of the situation and commits to specific follow-through"},
                            {"n": 2, "title": "Builds structure and empowers the coachee", "dac": "Creates a clear accountability framework (check-ins, milestones) that empowers the coachee to self-manage"},
                            {"n": 3, "title": "Acts with integrity and follows through", "dac": "Closes the session with clear mutual commitments and a shared understanding of next steps"},
                        ]
                    },
                },
            },
            "cbi": {
                "name": "Competency-Based Interview",
                "short": "CBI",
                "candidate_role": "Officer / Manager (sharing real-world past experiences)",
                "competencies": {
                    "DSP": {
                        "kbis": [
                            {"n": 1, "title": "Drives results with clear business impact", "dac": "Shares a story where specific actions led to measurable business outcomes"},
                            {"n": 2, "title": "Sets direction and leads execution", "dac": "Describes leading a project or initiative with clear direction, standards, and follow-through"},
                        ]
                    },
                    "WTP": {
                        "kbis": [
                            {"n": 1, "title": "Handles underperformance with empathy and accountability", "dac": "Shares a story of managing a difficult or underperforming team member with both care and clear consequences"},
                            {"n": 2, "title": "Coaches and develops others", "dac": "Describes a specific instance of developing someone's skills or capability through coaching or mentoring"},
                            {"n": 3, "title": "Maintains team commitment under pressure", "dac": "Shares how they kept a team motivated and aligned during a difficult or high-pressure situation"},
                        ]
                    },
                    "LFDV": {
                        "kbis": [
                            {"n": 1, "title": "Proactively seeks and acts on feedback", "dac": "Shares a specific instance of asking for and meaningfully incorporating feedback from others"},
                            {"n": 2, "title": "Resolves disagreement through data and diverse input", "dac": "Describes navigating a conflict of views using evidence or by bringing in different perspectives"},
                            {"n": 3, "title": "Adjusts position when presented with better evidence", "dac": "Shares a time when they changed their stance based on a better idea or new information"},
                        ]
                    },
                    "MaD": {
                        "kbis": [
                            {"n": 1, "title": "Drives innovation or change despite resistance", "dac": "Shares a story of championing a new idea or process change and overcoming initial pushback"},
                            {"n": 2, "title": "Encourages others to try new approaches", "dac": "Describes how they created space for experimentation or learning in their team or organization"},
                        ]
                    },
                    "ET": {
                        "kbis": [
                            {"n": 1, "title": "Makes difficult decisions and owns the outcome", "dac": "Shares a situation requiring a hard judgment call and describes taking full accountability for the result"},
                            {"n": 2, "title": "Empowers others and builds accountability", "dac": "Describes delegating meaningfully to a team member and creating a follow-through structure"},
                        ]
                    },
                },
            },
        },
    },
    "first_loyalty": {
        "name": "First Loyalty",
        "activities": {
            "ap": {
                "name": "Analysis Presentation",
                "short": "AP",
                "candidate_role": "Account Manager (presenting to senior management)",
                "competencies": {
                    "DSP": {
                        "kbis": [
                            {"n": 1, "title": "Communicates clear recommendations and rationale", "dac": "Communicates clear recommendations and rationale aligned to business priorities"},
                            {"n": 2, "title": "Creates breakthrough strategies and practical actions", "dac": "Develops strong strategies and practical actions to improve business performance"},
                            {"n": 3, "title": "Acts with the customer in mind", "dac": "Considers customer impact and commercial implications in decisions"},
                            {"n": 4, "title": "Anticipates risks and opportunities early", "dac": "Recognizes risks and opportunities early and recommends timely business action"},
                        ]
                    },
                    "MaD": {
                        "kbis": [
                            {"n": 1, "title": "Drives change with practical improvements", "dac": "Suggests practical improvements to current business challenges"},
                            {"n": 2, "title": "Takes initiative despite incomplete information", "dac": "Takes initiative in addressing issues despite incomplete information"},
                            {"n": 3, "title": "Tests alternatives and adapts", "dac": "Tests alternatives, adapts recommendations, and incorporates broader perspectives"},
                        ]
                    },
                    "ET": {
                        "kbis": [
                            {"n": 1, "title": "Makes clear and timely decisions", "dac": "Makes clear and timely decisions, takes accountability, and demonstrates ownership"},
                            {"n": 2, "title": "Balances short-term and long-term stewardship", "dac": "Balances short-term decisions with long-term business impact and protection of company reputation"},
                            {"n": 3, "title": "Encourages cross-functional collaboration", "dac": "Encourages cross-functional collaboration and supports decisions using relevant data and expertise"},
                        ]
                    },
                },
            },
            "neg": {
                "name": "Negotiation Role Play",
                "short": "NEG",
                "candidate_role": "Account Manager (managing a client escalation / negotiation)",
                "competencies": {
                    "DSP": {
                        "kbis": [
                            {"n": 1, "title": "Identifies the most important issue and prioritizes action", "dac": "Identifies the most important issue and prioritizes action to protect the client relationship"},
                            {"n": 2, "title": "Provides practical, well-structured solutions", "dac": "Provides practical, well-structured solutions with clear rationale"},
                            {"n": 3, "title": "Balances customer needs and company interests", "dac": "Balances customer needs, commercial impact, and company interests in decisions"},
                            {"n": 4, "title": "Recognizes opportunities to strengthen partnership", "dac": "Recognizes opportunities to strengthen the long-term partnership beyond issue resolution"},
                        ]
                    },
                    "WTP": {
                        "kbis": [
                            {"n": 1, "title": "Builds rapport and manages with empathy", "dac": "Builds rapport and manages the conversation with empathy, professionalism, and respect"},
                            {"n": 2, "title": "Rebuilds confidence and secures commitment", "dac": "Rebuilds confidence and gains commitment toward sustained partnership and next steps"},
                            {"n": 3, "title": "Sets clear expectations and addresses accountability", "dac": "Sets clear expectations and addresses performance concerns through defined accountability"},
                            {"n": 4, "title": "Builds shared ownership and buy-in", "dac": "Builds client buy-in by creating shared ownership and commitment to agreed actions"},
                        ]
                    },
                    "LFDV": {
                        "kbis": [
                            {"n": 1, "title": "Asks thoughtful questions and listens actively", "dac": "Asks thoughtful questions and listens actively to understand the client's concerns"},
                            {"n": 2, "title": "Shares views and provides constructive challenge", "dac": "Shares views clearly and provides constructive challenge while maintaining openness"},
                            {"n": 3, "title": "Draws on client's perspective to improve decisions", "dac": "Draws on the client's perspective and uses it to improve decisions and next steps"},
                        ]
                    },
                    "ET": {
                        "kbis": [
                            {"n": 1, "title": "Takes clear ownership and follows through", "dac": "Takes clear ownership of issues and follows through on commitments"},
                            {"n": 2, "title": "Balances recovery with long-term stewardship", "dac": "Balances immediate client recovery with long-term business impact and protection of company reputation"},
                            {"n": 3, "title": "Enables confident, well-informed decisions", "dac": "Enables confident, well-informed decisions by establishing clear ownership and accountability"},
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
    activity = get_activity(program_code, activity_code)
    if not activity:
        return ""
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
    if not activity:
        return []
    return list(activity["competencies"].keys())
