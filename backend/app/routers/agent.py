"""
Agent router — handles chat, scoring, and block polish endpoints.

POST /api/agent/chat        → full turn: multi-extraction + reply + score + polish
POST /api/agent/score       → score one question against its suggestions
POST /api/agent/polish      → repolish one panel block
POST /api/agent/reset       → reset session state (new chat session)
GET  /api/agent/questions   → return full question list (for frontend bootstrap)
"""
import logging

from fastapi import APIRouter

from app.core.questions import QUESTIONS, Q_MAP, PANELS, get_active_question_ids

logger = logging.getLogger(__name__)
from app.models.agent import (
    ChatRequest,
    ChatResponse,
    Message,
    PolishRequest,
    QuestionsResponse,
    ScoreRequest,
)
from app.services.agent import (
    agent_reply,
    detect_topic_jump,
    polish_block,
    extract_multi_question_answers,
)
from app.services.scoring import (
    aggregate_approval,
    panel_score,
    score_against_suggestions,
    check_coverage,
)

router = APIRouter(prefix="/api/agent", tags=["agent"])


# ── ENDPOINTS ─────────────────────────────────────────────────────────────────

@router.get("/questions", response_model=QuestionsResponse)
async def get_questions():
    """Return full questions list and panel metadata for frontend bootstrapping."""
    return {
        "questions": [
            {
                "id": q.id,
                "panel": q.panel,
                "field": q.field,
                "label": q.label,
                "mandatory": q.mandatory,
                "weight": q.weight,
                "q": q.q,
                "suggestions": q.suggestions,
                "hints": q.hints,
                "isConditionalTrigger": q.is_conditional_trigger,
                "conditionalOn": {
                    "qid": q.conditional_on.qid,
                    "kws": q.conditional_on.kws,
                } if q.conditional_on else None,
            }
            for q in QUESTIONS
        ],
        "panels": PANELS,
    }


@router.post("/reset")
async def reset_session():
    """
    Signal a new chat session. No server state to clear (stateless API).
    Frontend uses this as a clean checkpoint for logging/audit.
    Returns the initial state shape so frontend can reset cleanly.
    """
    return {
        "status": "reset",
        "pending_q_id": QUESTIONS[0].id if QUESTIONS else "AI-Q1",
        "raw_answers": {},
        "conf_scores": {},
        "blocks": {"system": "", "user": "", "tech": ""},
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Full agentic turn with multi-question extraction:
    1. Multi-question extraction — parse the user message for answers to multiple questions at once
    2. Detect single topic jump if only one question extracted
    3. Get agent reply scoped to the primary (pending) question
    4. Accumulate all extracted answers into raw_answers
    5. Score all updated questions against their suggestions
    6. Polish all affected panel blocks
    7. Coverage check on primary question for follow-up logic
    8. Compute aggregate scores
    """
    raw_answers  = dict(req.raw_answers)
    pending_q_id = req.pending_q_id
    conf_scores  = dict(req.conf_scores)
    messages     = [m.model_dump() for m in req.messages]
    print("=== Chat Request ===")
    print(req.json())
    logger.info("Chat turn  pending=%s  answered=%d  history=%d msgs",
                pending_q_id, len(raw_answers), len(messages))

    user_text = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
    )

    active_ids = get_active_question_ids(raw_answers)

    # ── 1. Multi-question extraction ─────────────────────────────────────────
    # Try to find answers to multiple questions in one message
    extractions: dict[str, str] = {}
    if pending_q_id and user_text:
        extractions = await extract_multi_question_answers(
            user_text, pending_q_id, active_ids, raw_answers
        )

    logger.info("Extracted %d question(s): %s", len(extractions), list(extractions.keys()))

    # ── 2. Determine effective primary question ───────────────────────────────
    effective_q_id = pending_q_id

    if len(extractions) == 1 and pending_q_id:
        # Single extraction — may be a topic jump
        only_qid = next(iter(extractions))
        if only_qid != pending_q_id and only_qid in active_ids:
            effective_q_id = only_qid

    elif len(extractions) > 1:
        # Multi-extraction — keep pending as primary for the reply context
        # but all extracted questions will be saved
        effective_q_id = pending_q_id

    # ── 3. Agent reply ────────────────────────────────────────────────────────
    reply = await agent_reply(messages, raw_answers, active_ids, effective_q_id)


    print("=== Agent Reply ===")
    print(reply)
    # ── 4. Accumulate all extracted answers ───────────────────────────────────
    updated_q_ids: list[str] = []
    extraction_summary: list[dict] = []

    for qid, extracted_text in extractions.items():
        q_cfg = Q_MAP.get(qid)
        if not q_cfg:
            continue
        prev = raw_answers.get(qid, "")
        raw_answers[qid] = f"{prev} {extracted_text}".strip() if prev else extracted_text.strip()
        updated_q_ids.append(qid)
        extraction_summary.append({
            "qid": qid,
            "label": q_cfg.label,
            "text": raw_answers[qid],
        })

    print("=== Updated Raw Answers After Extraction ===")
    print(raw_answers)
    print("extraction summary")
    print(extraction_summary)
    # Fallback: if nothing was extracted and we have a pending question, save raw
    # But skip pure filler/acknowledgment messages
    _FILLER = {"ok", "okay", "sure", "thanks", "thank you", "got it", "alright",
               "fine", "cool", "right", "hmm", "i see", "noted", "yes", "no", "yep", "nope"}
    if not updated_q_ids and pending_q_id and user_text:
        is_filler = user_text.strip().lower().rstrip(".,!?") in _FILLER
        q_cfg = Q_MAP.get(pending_q_id)
        if q_cfg and not is_filler:
            prev = raw_answers.get(pending_q_id, "")
            raw_answers[pending_q_id] = f"{prev} {user_text}".strip() if prev else user_text.strip()
            updated_q_ids.append(pending_q_id)

    # Recompute active IDs after saving (AI-Q15 may open new questions)
    active_ids = get_active_question_ids(raw_answers)
    print("=== Active Questions After Extraction ===")
    print(active_ids)
    # ── 5. Score all updated questions ────────────────────────────────────────
    new_scores: dict[str, float] = {}
    for qid in updated_q_ids:
        result = await score_against_suggestions(qid, raw_answers[qid])
        new_scores[qid] = result["score"]

    logger.info("Scores this turn: %s", {k: round(v, 2) for k, v in new_scores.items()})
    print("=== New Scores ===")
    print(new_scores)

    # Merge into full conf_scores (frontend sends these back each turn)
    conf_scores.update(new_scores)
    print("=== Updated Confidence Scores ===")
    print(conf_scores)
    # ── 6. Polish all affected panels ─────────────────────────────────────────
    affected_panels = {Q_MAP[qid].panel for qid in updated_q_ids if qid in Q_MAP}
    polished_blocks: dict[str, str] = {}
    for panel in affected_panels:
        panel_answers = {
            q.id: raw_answers[q.id]
            for q in QUESTIONS
            if q.panel == panel and q.id in raw_answers
        }
        polished_blocks[panel] = await polish_block(panel, panel_answers)

    print("=== Polished Blocks ===")
    print(polished_blocks)
    # ── 7. Coverage check on primary question ─────────────────────────────────
    coverage_ok     = True
    missing_suggestions: list[str] = []
    primary_answer  = raw_answers.get(effective_q_id, "") if effective_q_id else ""
    if effective_q_id and primary_answer:
        cov = await check_coverage(effective_q_id, primary_answer)
        coverage_ok         = cov["coverageOk"]
        missing_suggestions = cov["missingSuggestions"]

    print("confidence scores")
    print(conf_scores)
    print("raw answers")
    print(raw_answers)
    print("coverage check")
    print({
        "coverage_ok": coverage_ok,
        "missing_suggestions": missing_suggestions
    })
    # ── 8. Aggregate scores ───────────────────────────────────────────────────
    total_score = aggregate_approval(conf_scores, raw_answers)
    panel_scores_map = {p: panel_score(p, conf_scores, raw_answers) for p in PANELS}

    # Nudge on weak answer — mandatory questions use configured threshold,
    # non-mandatory questions nudge when score is very low (< 0.3)
    from app.core.config import settings
    is_nudge  = False
    nudge_text = ""
    pq = Q_MAP.get(effective_q_id) if effective_q_id else None
    primary_score = new_scores.get(effective_q_id, 0.0)
    if pq and effective_q_id in new_scores:
        threshold = settings.mandatory_threshold if pq.mandatory else 0.3
        if primary_score < threshold:
            is_nudge   = True
            nudge_text = missing_suggestions[0] if missing_suggestions else pq.suggestions[0]

    logger.info("Total score=%.1f%%  effective_q=%s  nudge=%s",
                total_score * 100, effective_q_id, is_nudge)

    return ChatResponse(
        reply=reply,
        effective_q_id=effective_q_id,
        updated_q_ids=updated_q_ids,
        new_answer=raw_answers.get(effective_q_id, ""),
        new_raw_answers=raw_answers,
        scores=new_scores,
        total_score=total_score,
        panel_scores=panel_scores_map,
        polished_blocks=polished_blocks,
        primary_panel=Q_MAP[effective_q_id].panel if effective_q_id and effective_q_id in Q_MAP else "",
        coverage_ok=coverage_ok,
        missing_suggestions=missing_suggestions,
        is_nudge=is_nudge,
        nudge_text=nudge_text,
        extraction_summary=extraction_summary,
    )


@router.post("/score")
async def score_question(req: ScoreRequest):
    """Score a single question answer against its suggestions."""
    result = await score_against_suggestions(req.question_id, req.user_text)
    return {
        "question_id": req.question_id,
        "score": result["score"],
        "analysis": result["analysis"],
    }


@router.post("/polish")
async def polish_panel(req: PolishRequest):
    """Re-polish a panel block from raw answers."""
    content = await polish_block(req.panel, req.raw_answers)
    return {"panel": req.panel, "content": content}

