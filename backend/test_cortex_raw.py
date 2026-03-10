"""Debug: inspect raw Cortex API response structure."""
import asyncio
import httpx
import json
from app.core.config import settings
from app.core.llm import _get_oauth_token


async def main():
    token = await _get_oauth_token()
    print(f"Token obtained: {token[:20]}...")

    url = f"{settings.cortex_api_url}/{settings.cortex_model}"
    query = "What is 2+2? Reply with just the number."
    params = {"q": query, "stream": "false", "no_summary": "true"}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    print(f"\nURL: {url}")
    print(f"Params: {params}")

    async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
        resp = await client.get(url, params=params, headers=headers)
        print(f"\nStatus: {resp.status_code}")
        print(f"Headers: {dict(resp.headers)}")
        
        raw_text = resp.text
        print(f"\nRaw response text (first 2000 chars):")
        print(raw_text[:2000])
        
        try:
            data = resp.json()
            print(f"\nJSON keys: {list(data.keys())}")
            for key, val in data.items():
                val_str = str(val)
                print(f"  {key}: {val_str[:200]}{'...' if len(val_str) > 200 else ''}")
        except Exception as e:
            print(f"\nFailed to parse JSON: {e}")


asyncio.run(main())
