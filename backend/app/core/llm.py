"""
Thin async wrapper around the Cortex LLM API with OAuth token auth.
"""
import json
import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

_cached_token: str | None = None


async def _get_oauth_token() -> str:
    """
    Obtain an OAuth token from Azure AD using client credentials.
    Caches the token for reuse within the process lifetime.
    """
    global _cached_token
    if _cached_token:
        return _cached_token

    oauth_url = (
        f"https://login.microsoftonline.com/{settings.cortex_tenant_id}/oauth2/v2.0/token"
    )
    payload = {
        "client_id": settings.cortex_client_id,
        "client_secret": settings.cortex_client_secret,
        "grant_type": "client_credentials",
        "scope": "api://Cortex_Engineering.lilly.com/.default",
    }

    async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
        resp = await client.post(oauth_url, data=payload)
        resp.raise_for_status()
        _cached_token = resp.json()["access_token"]
        logger.info("Cortex OAuth token obtained successfully")
        return _cached_token


async def call_llm(
    messages: list[dict],
    system: str,
    max_tokens: int = 800,
) -> str:
    """
    Build a prompt from system + messages, send it to the Cortex model/ask API,
    and return the response text.
    """
    # Build a single query string from system prompt + conversation
    parts = [f"[System]: {system}"]
    for m in messages:
        role = m.get("role", "user").capitalize()
        parts.append(f"[{role}]: {m['content']}")
    query = "\n".join(parts)

    token = await _get_oauth_token()
    url = f"{settings.cortex_api_url}/{settings.cortex_model}"
    params = {"q": query, "stream": "false", "no_summary": "false"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    logger.info("Cortex LLM call  model=%s  query_len=%d", settings.cortex_model, len(query))

    async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        print("dataaaaaa")
        print(data)
        reply = data.get("message", "")
        logger.info("Cortex LLM done  response_len=%d", len(reply))
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
