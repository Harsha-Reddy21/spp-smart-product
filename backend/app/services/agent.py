"""
SAGE Agent service — system prompt builder, topic jump detection, block polishing.
"""
from app.core.config import settings
from app.core.questions import QUESTIONS, Q_MAP, PANELS, get_active_question_ids
from app.core.llm import call_llm, parse_json


# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────

def build_system_prompt(raw_answers: dict, active_ids: set, pending_q_id: str | None) -> str:
    """
    Build the agent system prompt for the current turn.
    Mirrors buildSys() from the React frontend exactly.
    """
    pending = Q_MAP.get(pending_q_id) if pending_q_id else None

    collected_lines = "\n".join(
        f"  {qid} ({Q_MAP[qid].label}): \"{v}\""
        for qid, v in raw_answers.items()
        if qid in Q_MAP
    ) or "  Nothing yet"

    if not pending:
        return f"""You are SAGE — an AI Governance assistant.
All questions collected. Warmly congratulate the user and briefly summarise what was captured. 3-4 sentences, plain text only.
COLLECTED:
{collected_lines}"""

    current_answer = raw_answers.get(pending.id, "")
    suggestion_lines = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(pending.suggestions))

    if current_answer:
        answer_context = f"""ANSWER SO FAR: "{current_answer}"
→ Check which suggestions above are NOT yet covered in this answer.
→ Ask ONE short follow-up about the FIRST uncovered suggestion only.
→ Do NOT ask about anything not in the suggestions list."""
    else:
        answer_context = "→ Ask the question naturally. Keep it conversational."

    panel_label = PANELS.get(pending.panel, {}).get("label", pending.panel)

    return f"""You are SAGE — an AI Governance form-filling assistant.

CURRENT QUESTION: "{pending.label}"
ASK: "{pending.q}"
MANDATORY: {"YES" if pending.mandatory else "No"}
{"⚠ This is a Yes/No question — accept informal answers." if pending.is_conditional_trigger else ""}

REQUIRED SUGGESTIONS (the answer must cover all of these):
{suggestion_lines}

{answer_context}

STRICT RULES:
- Your follow-up questions must come ONLY from the suggestions list above — never invent new topics
- 2-3 sentences max
- NEVER mention question IDs
- When all suggestions are covered: say "Got it, noted for your {panel_label} block." and stop asking
- If user jumps to a different topic, acknowledge it and ask about THAT topic's suggestions

ALREADY COLLECTED (do not re-ask these):
{collected_lines}"""


# ── MULTI-QUESTION EXTRACTION ────────────────────────────────────────────────

async def extract_multi_question_answers(
    user_message: str,
    current_q_id: str,
    active_ids: set,
    raw_answers: dict,
) -> dict[str, str]:
    """
    Given a single user message that may answer multiple questions at once,
    extract per-question answers keyed by question ID.

    Example: "My system is called SmartAI, owned by John Smith in IT, and we don't use personal data"
    Returns: {"AI-Q1": "SmartAI", "AI-Q2": "John Smith in IT", "AI-Q15": "No"}

    Always includes the current question if any content is relevant to it.
    Falls back to {current_q_id: user_message} on failure so saves never break.
    """
    all_q = [q for q in QUESTIONS if q.id in active_ids]
    q_list = "\n".join(
        f'{q.id} ({q.label}): {q.q}'
        for q in all_q
    )
    print("=== Active Questions for Extraction ===")
    print(q_list)
    current_q_label = Q_MAP[current_q_id].label if current_q_id in Q_MAP else current_q_id

    system = (
        "You extract answers from user messages for AI governance questions. "
        "Respond ONLY with valid JSON."
    )
    prompt = f"""A user sent this message in an AI governance form interview:
"{user_message}"

The current question being asked is: {current_q_id} — "{current_q_label}"

All available questions:
{q_list}

Extract the answer for EACH question the user's message addresses.
Rules:
- Only include questions where the message clearly provides a SUBSTANTIVE answer
- IGNORE filler, acknowledgments, or non-informative messages like "ok", "sure", "got it", "thanks", "yes" (unless it's a Yes/No question), "no" (unless it's a Yes/No question), "hmm", "alright", "fine", "cool", "I see", etc.
- If the entire message is just filler/acknowledgment, return an EMPTY extractions array: {{"extractions": []}}
- ALWAYS include {current_q_id} if the message has substantive content relevant to it
- Extract the exact relevant portion of the user's text for each question — do not paraphrase or add
- If the message only answers one question, return only that one
- For Yes/No questions, normalise to "Yes" or "No" if unambiguous

Return ONLY:
{{
  "extractions": [
    {{"qid": "AI-QXX", "extracted_text": "the exact portion answering that question"}},
    ...
  ]
}}"""

    try:
        raw = await call_llm(
            [{"role": "user", "content": prompt}],
            system,
            600,
        )
        parsed = parse_json(raw)
        print("=== Extraction Result ===")
        print(parsed)
        if parsed and "extractions" in parsed:
            result: dict[str, str] = {}
            valid_ids = set(active_ids)
            for item in parsed["extractions"]:
                qid  = item.get("qid", "")
                text = item.get("extracted_text", "").strip()
                if qid in valid_ids and text:
                    result[qid] = text
            if result:
                return result
    except Exception:
        pass

    # Fallback: attribute entire message to current question
    return {current_q_id: user_message} if current_q_id else {}


# ── TOPIC JUMP DETECTION ─────────────────────────────────────────────────────

async def detect_topic_jump(
    user_message: str,
    current_q_id: str,
    active_ids: set,
    raw_answers: dict,
) -> str | None:
    """
    Returns a different question_id if the user is clearly talking about a
    different topic. Returns None if staying on current question.
    Only used when the message targets a SINGLE question (not multi-extraction).
    """
    all_q = [q for q in QUESTIONS if q.id in active_ids]
    q_list = "\n".join(f'{q.id}: "{q.label}" — {q.q}' for q in all_q)
    current_label = Q_MAP[current_q_id].label if current_q_id in Q_MAP else current_q_id

    system = "You detect which AI governance question a user message is about. Respond ONLY with valid JSON."
    prompt = f"""The user sent this message: "{user_message}"

Current question: {current_q_id} — "{current_label}"

All available questions:
{q_list}

Is the user's message primarily about a DIFFERENT question than the current one?

Examples of topic jumps:
- Current=Business Owner, user says "let me talk about deployment" → jumped to Deployment
- Current=Value Proposition, user says "about the personal data — we don't use any" → jumped to AI-Q15
- Current=AI System Name, user says "let's do risk mitigation" → jumped to Risk Mitigation

Return ONLY:
{{
  "isTopicJump": true,
  "targetQId": "AI-QXX or null",
  "confidence": "high/medium/low"
}}

Rules:
- isTopicJump=false if user is answering the current question or asking a general question
- targetQId must be one of the IDs listed above, or null
- Only flag jump if confidence is high or medium"""

    try:
        raw = await call_llm([{"role": "user", "content": prompt}], system, settings.topic_max_tokens)
        parsed = parse_json(raw)
        if parsed and parsed.get("isTopicJump") and parsed.get("targetQId") and parsed.get("confidence") != "low":
            target = parsed["targetQId"]
            if target in active_ids and target != current_q_id:
                return target
    except Exception:
        pass
    return None


# ── POLISH BLOCK ─────────────────────────────────────────────────────────────

async def polish_block(panel: str, raw_answers: dict) -> str:
    """
    Rewrite panel answers as clean professional prose.
    Anti-hallucination: only rephrase what user provided, never add facts.
    """
    qs = [q for q in QUESTIONS if q.panel == panel and q.id in raw_answers]
    if not qs:
        return ""

    print("=== Polishing Block ===")
    print('qssss')
    print(qs)
    field_summary = "\n".join(f'[{q.label}]: "{raw_answers[q.id]}"' for q in qs)
    panel_label = PANELS.get(panel, {}).get("label", panel)

    system = "You are an AI governance documentation editor. Rephrase only what the user provided. Never add assumptions. Respond ONLY with JSON."
    prompt = f"""Rephrase ONLY the information below into clean professional prose. Do not add anything not stated.

Raw input for "{panel_label}" block:
{field_summary}

Strict rules:
- Use ONLY facts stated above — nothing else
- Short input = short output (one field = one sentence max)
- No filler, no industry assumptions, no elaboration
- Natural flowing prose, no labels or bullets

Return ONLY: {{"content": "polished text"}}"""

    try:
        raw = await call_llm([{"role": "user", "content": prompt}], system, settings.polish_max_tokens)
        parsed = parse_json(raw)
        print("=== Polishing Result ===")
        print(parsed)
        return parsed.get("content", "") if parsed else ""
    except Exception:
        return ""


# ── AGENT REPLY ──────────────────────────────────────────────────────────────

async def agent_reply(
    messages: list[dict],
    raw_answers: dict,
    active_ids: set,
    pending_q_id: str | None,
) -> str:
    """Get next agent message given the conversation history."""
    system = build_system_prompt(raw_answers, active_ids, pending_q_id)
    return await call_llm(messages, system, settings.agent_max_tokens)
