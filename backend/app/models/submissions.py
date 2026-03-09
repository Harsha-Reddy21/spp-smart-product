from pydantic import BaseModel


class SubmitRequest(BaseModel):
    raw_answers: dict[str, str]
    conf_scores: dict[str, float]
    blocks: dict[str, str]          # {panel: polished_text}


class SubmitResponse(BaseModel):
    submission_id: str
    total_score: float
    panel_scores: dict
    created_at: str
