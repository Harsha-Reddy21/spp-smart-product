# SAGE — AI Governance & Evaluation

Agentic AI registration assistant. Chat-driven form filling with real-time confidence scoring.

---

## Project Structure

```
sage/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app + CORS + routers
│   │   ├── core/
│   │   │   ├── config.py              # Settings (scoring constants, model name)
│   │   │   ├── llm.py                 # Anthropic API wrapper (httpx async)
│   │   │   └── questions.py           # All 22 questions — single source of truth
│   │   ├── services/
│   │   │   ├── agent.py               # System prompt builder, topic detection, polish
│   │   │   └── scoring.py             # aggregate_approval(), score_against_suggestions()
│   │   └── routers/
│   │       ├── agent.py               # POST /api/agent/chat, /score, /polish, GET /questions
│   │       └── submissions.py         # POST /api/submissions/submit, GET /list, GET /{id}
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── main.jsx                   # React entry point
    │   ├── App.jsx                    # Main layout + all state + send logic
    │   ├── api/index.js               # All fetch() calls to backend
    │   ├── hooks/questions.js         # Question registry + scoring (mirrors backend)
    │   └── components/Block.jsx       # Editable panel block component
    ├── index.html
    ├── package.json
    └── vite.config.js                 # Proxies /api → localhost:8000
```

---

## Setup

### Backend

```bash
cd sage/backend

# Copy env and add your API key
cp .env.example .env
# Edit .env: ANTHROPIC_API_KEY=sk-ant-...

# Install dependencies
pip install -r requirements.txt

# Run
uvicorn app.main:app --reload --port 8000
```

Backend available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Frontend

```bash
cd sage/frontend

npm install
npm run dev
```

Frontend available at: http://localhost:5173

Vite proxies all `/api/*` requests to `http://localhost:8000`.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET    | `/health` | Health check |
| GET    | `/api/agent/questions` | Full question list + panel metadata |
| POST   | `/api/agent/chat` | Full agent turn (topic jump + reply + score + polish) |
| POST   | `/api/agent/score` | Score one question against suggestions |
| POST   | `/api/agent/polish` | Re-polish one panel block |
| POST   | `/api/submissions/submit` | Persist completed evaluation |
| GET    | `/api/submissions/list` | List all submissions |
| GET    | `/api/submissions/{id}` | Get single submission |

### POST /api/agent/chat

Request:
```json
{
  "messages": [{"role": "user", "content": "Smart Product Profile"}],
  "raw_answers": {"AI-Q1": "Smart Product Profile"},
  "pending_q_id": "AI-Q2"
}
```

Response:
```json
{
  "reply": "Great name! Who is the business owner...",
  "effective_q_id": "AI-Q2",
  "new_answer": "Smart Product Profile",
  "new_raw_answers": {"AI-Q1": "Smart Product Profile"},
  "score": 0.75,
  "total_score": 0.12,
  "panel_scores": {"user": 0.75, "system": null, "tech": null},
  "polished_block": "The AI system is named Smart Product Profile.",
  "panel": "user",
  "coverage_ok": true,
  "missing_suggestions": [],
  "is_nudge": false,
  "nudge_text": ""
}
```

---

## Architecture Decisions

### Direct answer accumulation (no LLM gate)
User text is **always** saved immediately when a message arrives. There is no LLM call that decides whether to save — that was the root cause of answers not appearing in the UI. The LLM is only called *after* saving, to score and check coverage.

### Topic jump detection
Before the agent replies, a lightweight LLM call checks whether the user is jumping to a different question ("let's talk about deployment"). If detected with medium/high confidence, `pendingQId` jumps to the matched question, and all downstream processing (reply, score, polish) targets the new question.

### Suggestions-driven scoring
Coverage scoring uses `suggestions[]` from `sage_ai_suggestions.csv` — the exact same field that `analyze_suggestions_coverage()` in `scoring_service.py` uses. Agent follow-ups are also locked to these suggestions only (never invented topics).

### Scoring mirrors backend exactly
`aggregateApproval()` in `hooks/questions.js` is a direct JavaScript port of `aggregate_approval()` from `scoring_service.py`:
- Mandatory threshold: 0.6
- Static penalty: 0.15 (compounding per failing mandatory question)
- Default mandatory confidence: 0.3 (for unanswered mandatory questions)
- Missing policy: IGNORE_AND_RENORM

### Conditional questions
- AI-Q20, AI-Q22, AI-Q23 are hidden until AI-Q15 = "Yes"
- AI-Q23 is hidden unless AI-Q22 = "No" or "Yes - a sampling"

---

## Production Notes

- Replace `_store` dict in `submissions.py` with SQLAlchemy + PostgreSQL
- Add authentication (JWT) to the API routers
- Move `ANTHROPIC_API_KEY` to a secrets manager
- Add rate limiting to `/api/agent/chat`
- The frontend currently holds `conf_scores` in React state — in production, persist these per submission in the DB and reload on page refresh
