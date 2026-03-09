"""Quick API smoke tests for the SAGE backend."""
import httpx
import asyncio
import json
import sys


async def main():
    base = "http://localhost:8000"
    passed = 0
    failed = 0

    async with httpx.AsyncClient(base_url=base, timeout=60.0) as c:

        # ── TEST 1: GET /api/agent/questions ──────────────────────────────
        print("=== TEST 1: GET /api/agent/questions ===")
        r = await c.get("/api/agent/questions")
        print(f"Status: {r.status_code}")
        assert r.status_code == 200, f"FAIL: status {r.status_code}"
        d = r.json()
        q_count = len(d["questions"])
        print(f"Questions count: {q_count}")
        print(f"Panels: {list(d['panels'].keys())}")
        ids = [q["id"] for q in d["questions"]]
        first = d["questions"][0]
        print(f"First Q: {first['id']} - {first['label']} (panel={first['panel']})")

        assert "AI-Q1" not in ids, "FAIL: AI-Q1 should be removed!"
        assert ids[0] == "AI-Q2", f"FAIL: first should be AI-Q2, got {ids[0]}"
        assert q_count == 23, f"FAIL: expected 23 questions, got {q_count}"

        # Conditional check
        cond_q7 = next(q for q in d["questions"] if q["id"] == "AI-Q7")
        assert cond_q7["conditionalOn"]["qid"] == "AI-Q6", "FAIL: AI-Q7 conditional wrong"
        print("PASS\n")
        passed += 1

        # ── TEST 2: POST /api/agent/reset ─────────────────────────────────
        print("=== TEST 2: POST /api/agent/reset ===")
        r = await c.post("/api/agent/reset")
        print(f"Status: {r.status_code}")
        assert r.status_code == 200, f"FAIL: status {r.status_code}"
        d = r.json()
        print(f"Response: {json.dumps(d, indent=2)}")
        assert d["status"] == "reset"
        assert d["pending_q_id"] == "AI-Q2", f"FAIL: pending should be AI-Q2, got {d['pending_q_id']}"
        print("PASS\n")
        passed += 1

        # ── TEST 3: POST /api/agent/chat (real LLM call via Cortex) ──────
        print("=== TEST 3: POST /api/agent/chat ===")
        print("Sending: 'The system is called SmartPredict'")
        payload = {
            "messages": [
                {"role": "assistant", "content": "What is the title of your System?"},
                {"role": "user", "content": "The system is called SmartPredict"},
            ],
            "raw_answers": {},
            "pending_q_id": "AI-Q2",
            "conf_scores": {},
        }
        r = await c.post("/api/agent/chat", json=payload)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            d = r.json()
            print(f"Reply: {d['reply'][:200]}...")
            print(f"Effective Q: {d['effective_q_id']}")
            print(f"Updated Qs: {d['updated_q_ids']}")
            print(f"New raw answers keys: {list(d['new_raw_answers'].keys())}")
            print(f"Scores: {d['scores']}")
            print(f"Total score: {d['total_score']}")
            print(f"Polished blocks keys: {list(d['polished_blocks'].keys())}")
            assert d["effective_q_id"] is not None, "FAIL: no effective_q_id"
            assert len(d["updated_q_ids"]) > 0, "FAIL: no questions updated"
            print("PASS\n")
            passed += 1
        else:
            print(f"FAIL: {r.status_code} - {r.text[:500]}")
            failed += 1

        # ── TEST 4: POST /api/agent/score ─────────────────────────────────
        print("=== TEST 4: POST /api/agent/score ===")
        payload = {
            "question_id": "AI-Q2",
            "user_text": "SmartPredict - an AI-powered predictive analytics system",
        }
        r = await c.post("/api/agent/score", json=payload)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            d = r.json()
            print(f"Score result: {json.dumps(d, indent=2)}")
            assert "score" in d, "FAIL: no score in response"
            assert 0.0 <= d["score"] <= 1.0, f"FAIL: score out of range: {d['score']}"
            print("PASS\n")
            passed += 1
        else:
            print(f"FAIL: {r.status_code} - {r.text[:500]}")
            failed += 1

    print(f"{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
