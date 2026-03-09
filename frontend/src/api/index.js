/**
 * SAGE API client — all fetch calls go through here.
 * Vite proxies /api → http://localhost:8000
 */

const BASE = "/api";

async function post(path, body) {
  const r = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const err = await r.text();
    throw new Error(`API ${path} failed (${r.status}): ${err}`);
  }
  return r.json();
}

async function get(path) {
  const r = await fetch(`${BASE}${path}`);
  if (!r.ok) throw new Error(`API GET ${path} failed (${r.status})`);
  return r.json();
}

/**
 * Main chat turn — multi-question extraction + reply + score + polish.
 * @param {Array}  messages     Full conversation history
 * @param {Object} rawAnswers   {questionId: answerText}
 * @param {string} pendingQId   Currently active question ID
 * @param {Object} confScores   {questionId: score} — all previous scores
 */
export async function chat(messages, rawAnswers, pendingQId, confScores = {}) {
  return post("/agent/chat", {
    messages,
    raw_answers: rawAnswers,
    pending_q_id: pendingQId,
    conf_scores: confScores,
  });
}

/**
 * Score a single question answer against its suggestions.
 */
export async function scoreQuestion(questionId, userText) {
  return post("/agent/score", { question_id: questionId, user_text: userText });
}

/**
 * Re-polish one panel block from current raw answers.
 */
export async function polishPanel(panel, rawAnswers) {
  return post("/agent/polish", { panel, raw_answers: rawAnswers });
}

/**
 * Reset session — clears server-side log and returns initial state shape.
 * Actual state reset lives in the frontend.
 */
export async function resetSession() {
  return post("/agent/reset", {});
}

/**
 * Submit a completed evaluation for persistence.
 */
export async function submitEvaluation(rawAnswers, confScores, blocks) {
  return post("/submissions/submit", {
    raw_answers: rawAnswers,
    conf_scores: confScores,
    blocks,
  });
}

/**
 * Fetch all past submissions.
 */
export async function listSubmissions() {
  return get("/submissions/list");
}

/**
 * Fetch question list from backend (used on mount to keep frontend in sync).
 */
export async function getQuestions() {
  return get("/agent/questions");
}

