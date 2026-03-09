from pydantic import BaseModel


class Message(BaseModel):
    role: str   # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]           # full conversation history including latest user msg
    raw_answers: dict[str, str]       # {question_id: answer_text}
    pending_q_id: str | None          # currently active question ID
    conf_scores: dict[str, float] = {}  # all previous conf scores from frontend


class ChatResponse(BaseModel):
    reply: str
    effective_q_id: str | None        # primary question updated this turn
    updated_q_ids: list[str]          # ALL questions updated (may be >1 for multi-extraction)
    new_answer: str                   # accumulated answer for primary question
    new_raw_answers: dict             # full updated raw_answers
    scores: dict[str, float]          # {qid: score} — all questions scored this turn
    total_score: float
    panel_scores: dict
    polished_blocks: dict[str, str]   # {panel: polished_text} — may update multiple panels
    primary_panel: str
    coverage_ok: bool
    missing_suggestions: list[str]
    is_nudge: bool
    nudge_text: str
    extraction_summary: list[dict]    # [{qid, label, text}] for UI acknowledgement


class ScoreRequest(BaseModel):
    question_id: str
    user_text: str


class PolishRequest(BaseModel):
    panel: str
    raw_answers: dict[str, str]


class QuestionsResponse(BaseModel):
    questions: list[dict]
    panels: dict
