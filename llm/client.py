"""
LLM client for DevPulse.
Supports Gemini (Google Antigravity SDK) and Hugging Face (Qwen2.5-VL) backends.
"""
import os
import json
import logging
import asyncio
from typing import Any, Type, TypeVar
from pydantic import BaseModel

# Note: google.antigravity has protobuf compatibility issues
# Using mock LLM by default. To enable real LLM, fix protobuf version.
# from google.antigravity import Agent, LocalAgentConfig

from config import MOCK_LLM, LLM_PROVIDER, LLM_MODEL, GOOGLE_API_KEY, HF_TOKEN, LOGS_DIR

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "llm_client.log"))
logger.setLevel(logging.INFO)

T = TypeVar("T", bound=BaseModel)

def _mock_analyzer_response(user_prompt: str) -> str:
    """Mock analyzer response dynamic generator for DevRel insights."""
    # Find the top topic in the prompt to make it dynamic
    top_topic = "API Design"
    lines = user_prompt.split('\n')
    for line in lines:
        if "avg_score=" in line:
            parts = line.strip().split(':')
            if len(parts) >= 2:
                name = parts[0].replace("-", "").strip()
                if name:
                    top_topic = name
                    break

    return json.dumps({
        "insights": [
            f"🎯 {top_topic} tutorials drive 45% higher developer conversions than standard documentation.",
            "💻 Code examples with runnable snippets have 3x the engagement rate of text-only guides.",
            "🛡️ Security and DevOps topics show the strongest long-term retention metrics.",
            "📈 Content length analysis shows that evergreen posts (3000+ words) get 60% more shares over 90 days."
        ]
    })

def _mock_predictor_response(user_prompt: str) -> str:
    """Mock predictor response dynamic generator based on draft input."""
    # Parse inputs from the prompt
    title = "Proposed Content"
    topic = "API Design"
    fmt = "technical_blog"
    audience = "developers"
    word_count = 1500

    for line in user_prompt.split('\n'):
        if line.startswith("Title:"):
            title = line.replace("Title:", "").strip()
        elif line.startswith("Topic:"):
            topic = line.replace("Topic:", "").strip()
        elif line.startswith("Format:"):
            fmt = line.replace("Format:", "").strip()
        elif line.startswith("Audience:"):
            audience = line.replace("Audience:", "").strip()
        elif line.startswith("Word count:"):
            try:
                word_count = int(line.replace("Word count:", "").strip())
            except:
                pass

    # Dynamic scoring rules
    base_score = 60
    # Length optimization
    if 1000 <= word_count <= 4000:
        base_score += 15
    elif word_count > 4000:
        base_score += 5
    
    # Title optimization
    title_lower = title.lower()
    if any(keyword in title_lower for keyword in ["tutorial", "guide", "how to", "master", "complete"]):
        base_score += 10
    if len(title) > 20:
        base_score += 5

    # Clamp score
    score = min(98, max(40, base_score + (hash(title) % 11 - 5)))

    suggestions = [
        f"✓ Include more runnable code snippets tailored for the {audience} segment.",
        f"✓ Add a troubleshooting or common errors section to increase developer trust.",
        f"✓ Optimize the header for search rankings targeting key '{topic}' terms."
    ]

    return json.dumps({
        "predicted_score": score,
        "reasoning": f"Your draft '{title}' on {topic} for {audience} shows strong semantic relevance. Word count of {word_count} is optimal. Suggestions aim to maximize conversions.",
        "suggestions": suggestions,
        "confidence": "high" if score >= 75 else "medium",
        "comparable_count": 6 + (hash(topic) % 8),
        "code_quality_feedback": "Good structuring detected.",
        "code_to_text_ratio": 0.28
    })

def _mock_generic_response() -> str:
    """Generic mock response."""
    return json.dumps({"status": "mock", "message": "Mock LLM response", "data": None})

async def _call_gemini_async(
    system_prompt: str, user_prompt: str,
    response_schema: Type[T] | None = None, max_tokens: int = 500
) -> Any:
    """Async call via Google Antigravity SDK."""
    config = LocalAgentConfig(
        model=LLM_MODEL,
        system_instructions=system_prompt,
        response_schema=response_schema,
    )
    async with Agent(config=config) as agent:
        response = await agent.chat(user_prompt)
        if response_schema:
            return await response.structured_output()
        return await response.text()

def _call_huggingface(
    system_prompt: str, user_prompt: str,
    response_schema: Type[T] | None = None, max_tokens: int = 500
) -> Any:
    """Call via Hugging Face Serverless API (OpenAI-compatible)."""
    from openai import OpenAI
    client = OpenAI(base_url="https://api-inference.huggingface.co/v1/", api_key=HF_TOKEN)
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-VL-7B-Instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=max_tokens,
    )
    text = response.choices[0].message.content
    if response_schema:
        return json.loads(text)
    return text

def call_llm(
    system_prompt: str, user_prompt: str,
    response_schema: Type[T] | None = None, max_tokens: int = 500
) -> Any:
    """
    Unified LLM call with mock fallback, Gemini, and HuggingFace support.
    """
    # Mock mode
    if MOCK_LLM:
        system_lower = system_prompt.lower()
        if "analyzer" in system_lower or "analytics" in system_lower:
            mock_str = _mock_analyzer_response()
        elif "predictor" in system_lower or "predict" in system_lower:
            mock_str = _mock_predictor_response()
        else:
            mock_str = _mock_generic_response()
        if response_schema:
            return response_schema(**json.loads(mock_str))
        return mock_str
    
    # Production call
    try:
        if LLM_PROVIDER == "huggingface":
            logger.info("Routing to Hugging Face (Qwen2.5-VL)")
            result = _call_huggingface(system_prompt, user_prompt, response_schema, max_tokens)
        else:
            logger.info("Routing to Google Antigravity SDK (Gemini)")
            result = asyncio.run(
                _call_gemini_async(system_prompt, user_prompt, response_schema, max_tokens)
            )
        if response_schema and isinstance(result, dict):
            return response_schema(**result)
        return result
    except Exception as e:
        logger.error(f"LLM call failed: {e}", exc_info=True)
        if response_schema:
            raise
        return json.dumps({"error": "LLM call failed", "details": str(e)})
