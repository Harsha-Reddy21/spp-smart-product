"""
Thin async wrapper around the OpenAI Chat Completions API.
"""
import json
import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


async def call_llm(
    messages: list[dict],
    system: str,
    max_tokens: int = 800,
) -> str:
    """
    Call OpenAI GPT and return the assistant reply text.
    Raises httpx.HTTPStatusError on non-2xx responses.
    """
    oai_messages = [{"role": "system", "content": system}] + messages
    logger.info("LLM call  model=%s  max_tokens=%d", settings.openai_model, max_tokens)
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "content-type": "application/json",
            },
            json={
                "model": settings.openai_model,
                "max_tokens": max_tokens,
                "messages": oai_messages,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        reply = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        logger.info("LLM done   tokens=%s", usage.get("total_tokens", "?"))
        return reply


def parse_json(raw: str) -> dict | None:
    """Extract and parse the first JSON object from a raw LLM response."""
    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        start = clean.index("{")
        end   = clean.rindex("}") + 1
        return json.loads(clean[start:end])
    except Exception:
        return None
