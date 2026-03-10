"""Debug: test raw Cortex LLM response format."""
import asyncio
from app.core.llm import call_llm, parse_json


async def main():
    # Test 1: Simple prompt to see raw response format
    system = "Respond ONLY with valid JSON."
    prompt = 'Return ONLY: {"content": "Smart Product Profile is the system title."}'

    print("=== TEST 1: Simple JSON response ===")
    result = await call_llm([{"role": "user", "content": prompt}], system, 200)
    print(f"Raw type: {type(result)}")
    print(f"Raw repr: {repr(result)}")
    print(f"Raw str:  {result}")
    parsed = parse_json(result)
    print(f"Parsed:   {parsed}")
    print()

    # Test 2: Score-like prompt
    system2 = "You are a coverage scoring engine. Respond ONLY with valid JSON."
    prompt2 = (
        'Analyze how well "Smart product profile" covers: '
        '"Provide a clear and descriptive title for the AI system". '
        'Return ONLY: {"score": 0.5, "suggestions_analysis": [{"text": "suggestion", "status": "completed", "rationale": "why"}]}'
    )
    print("=== TEST 2: Score response ===")
    result2 = await call_llm([{"role": "user", "content": prompt2}], system2, 500)
    print(f"Raw repr: {repr(result2)}")
    parsed2 = parse_json(result2)
    print(f"Parsed:   {parsed2}")
    print()

    # Test 3: Agent reply
    system3 = "You are SAGE. Ask the user: What is the title of your System? Keep it to 2 sentences."
    prompt3 = "Hello"
    print("=== TEST 3: Agent reply ===")
    result3 = await call_llm([{"role": "user", "content": prompt3}], system3, 200)
    print(f"Raw repr: {repr(result3)}")
    print(f"Raw str:  {result3}")


asyncio.run(main())
