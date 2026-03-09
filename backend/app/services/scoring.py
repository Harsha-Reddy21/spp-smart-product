"""
Scoring service — mirrors aggregate_approval() from scoring_service.py.
All logic is pure Python; no DB required for the standalone version.
"""
from app.core.config import settings
from app.core.questions import QUESTIONS, Q_MAP, get_active_question_ids
from app.core.llm import call_llm, parse_json


# ── AGGREGATE APPROVAL ────────────────────────────────────────────────────────

def aggregate_approval(conf_scores: dict[str, float], raw_answers: dict) -> float:
    """
    Weighted approval score with mandatory-question penalties.
    Mirrors aggregate_approval() from scoring_service.py exactly.

    conf_scores: {question_id: 0.0-1.0}
    raw_answers: {question_id: answer_text}  — used to determine active set
    """
    active_ids = get_active_question_ids(raw_answers)
    mandatory  = {q.id for q in QUESTIONS if q.mandatory and q.id in active_ids}

    MAND_THRESHOLD  = settings.mandatory_threshold
    STATIC_PENALTY  = settings.static_penalty
    DEFAULT_MAND_C  = settings.default_mandatory_confidence

    norm_c: dict[str, float] = {}
    included: list[str] = []
    total_w = 0.0

    for q in QUESTIONS:
        if q.id not in active_ids:
            continue
        raw = conf_scores.get(q.id)
        if raw is None:
            c = DEFAULT_MAND_C if q.id in mandatory else None
        else:
            c = max(0.0, min(1.0, raw))

        if c is None:
            continue   # IGNORE_AND_RENORM: skip missing non-mandatory

        norm_c[q.id] = c
        if q.weight > 0:
            included.append(q.id)
            total_w += q.weight

    if not included or total_w == 0:
        return 0.0

    base = sum((Q_MAP[qid].weight / total_w) * norm_c[qid] for qid in included)

    penalty = 1.0
    for qid in mandatory:
        if norm_c.get(qid, DEFAULT_MAND_C) < MAND_THRESHOLD:
            penalty *= (1.0 - STATIC_PENALTY)

    return min(1.0, base * penalty)


def panel_score(panel: str, conf_scores: dict, raw_answers: dict) -> float | None:
    """Weighted average score for a single panel."""
    active_ids = get_active_question_ids(raw_answers)
    qs = [q for q in QUESTIONS if q.panel == panel and q.id in active_ids and q.id in conf_scores]
    if not qs:
        return None
    total_w = sum(q.weight for q in qs)
    if total_w == 0:
        return None
    return sum((q.weight / total_w) * conf_scores[q.id] for q in qs)


# ── SUGGESTION COVERAGE SCORING ──────────────────────────────────────────────

async def score_against_suggestions(question_id: str, user_text: str) -> dict:
    """
    Ask the LLM how well user_text covers the required suggestions for question_id.
    Returns {"score": float, "analysis": list}
    Mirrors analyze_suggestions_coverage() from scoring_service.py.
    """
    q = Q_MAP.get(question_id)
    if not q or not user_text.strip():
        return {"score": 0.0, "analysis": []}

    suggestions_text = "\n".join(f"- {s}" for s in q.suggestions)
    system = "You are a coverage scoring engine for AI governance. Respond ONLY with valid JSON."
    prompt = f"""Analyze how well the user's answer covers the required suggestions.

Question: "{q.q}"

Required suggestions (from suggestions database):
{suggestions_text}

User's answer: "{user_text}"

Scoring scale:
1.0 = All suggestions thoroughly addressed
0.8 = Most suggestions well addressed
0.6 = About half addressed
0.4 = Few suggestions touched
0.2 = Barely addressed
0.0 = Not addressed at all

Return ONLY:
{{"score": 0.0, "suggestions_analysis": [{{"text": "suggestion", "status": "completed|required", "rationale": "why"}}]}}"""

    for _ in range(2):
        try:
            raw = await call_llm([{"role": "user", "content": prompt}], system, settings.score_max_tokens)
            parsed = parse_json(raw)
            if parsed and "score" in parsed:
                return {
                    "score": max(0.0, min(1.0, float(parsed["score"]))),
                    "analysis": parsed.get("suggestions_analysis", []),
                }
        except Exception:
            pass
    return {"score": settings.default_confidence, "analysis": []}


# ── COVERAGE CHECK (follow-up logic) ─────────────────────────────────────────

async def check_coverage(question_id: str, combined_text: str) -> dict:
    """
    Check which suggestions are still missing. Used for agent follow-up prompts.
    Does NOT gate saving. Returns {"coverageOk": bool, "missingSuggestions": list}.
    """
    q = Q_MAP.get(question_id)
    if not q or not combined_text.strip():
        return {"coverageOk": False, "missingSuggestions": q.suggestions if q else []}

    suggestions_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(q.suggestions))
    system = "You check suggestion coverage for AI governance answers. Respond ONLY with valid JSON."
    prompt = f"""Does this answer cover the required suggestions?

QUESTION: "{q.q}"
REQUIRED SUGGESTIONS:
{suggestions_text}

USER ANSWER: "{combined_text}"

coverageOk = true if at least one suggestion is meaningfully addressed.

Return ONLY:
{{"coverageOk": true, "missingSuggestions": ["exact text of suggestions NOT yet covered"]}}"""

    try:
        raw = await call_llm([{"role": "user", "content": prompt}], system, settings.coverage_max_tokens)
        parsed = parse_json(raw)
        if parsed:
            return {
                "coverageOk": bool(parsed.get("coverageOk", True)),
                "missingSuggestions": parsed.get("missingSuggestions", []),
            }
    except Exception:
        pass
    return {"coverageOk": True, "missingSuggestions": []}
