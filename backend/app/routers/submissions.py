"""
Submissions router — persist and retrieve completed evaluations.
Uses in-memory store; swap the store dict for SQLAlchemy in production.
"""
import logging
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

from app.core.questions import get_active_question_ids, PANELS
from app.models.submissions import SubmitRequest, SubmitResponse
from app.services.scoring import aggregate_approval, panel_score

router = APIRouter(prefix="/api/submissions", tags=["submissions"])

# In-memory store — replace with DB in production
_store: dict[str, dict] = {}


@router.post("/submit", response_model=SubmitResponse)
async def submit(req: SubmitRequest):
    """Persist a completed SAGE evaluation."""
    sub_id = str(uuid.uuid4())
    total  = aggregate_approval(req.conf_scores, req.raw_answers)
    p_scores = {p: panel_score(p, req.conf_scores, req.raw_answers) for p in PANELS}

    record = {
        "submission_id": sub_id,
        "raw_answers":   req.raw_answers,
        "conf_scores":   req.conf_scores,
        "blocks":        req.blocks,
        "total_score":   total,
        "panel_scores":  p_scores,
        "created_at":    datetime.now(timezone.utc).isoformat(),
    }
    _store[sub_id] = record
    logger.info("Submission saved  id=%s  score=%.1f%%  panels=%s",
                sub_id, total * 100, {k: round(v, 2) for k, v in p_scores.items()})
    return SubmitResponse(
        submission_id=sub_id,
        total_score=total,
        panel_scores=p_scores,
        created_at=record["created_at"],
    )


@router.get("/list")
async def list_submissions():
    """Return all submissions ordered newest first."""
    return sorted(_store.values(), key=lambda r: r["created_at"], reverse=True)


@router.get("/{submission_id}")
async def get_submission(submission_id: str):
    """Return a single submission by ID."""
    rec = _store.get(submission_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Submission not found")
    return rec
