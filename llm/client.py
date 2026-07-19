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

def _mock_analyzer_response() -> str:
    """Mock analyzer response for DevRel insights."""
    return json.dumps({
        "insights": [
            "API Design tutorials drive 45% higher developer signups than blog posts.",
            "Code examples with runnable snippets have 3x the engagement rate of text-only guides.",
            "Backend developers show the strongest conversion to API console signups.",
            "Content published after major framework releases sees 60% more views.",
            "Tutorial-format content under 1500 words has the highest completion rate.",
            "Authentication and OAuth guides have the highest search ranking performance.",
        ]
    })

def _mock_predictor_response() -> str:
    """Mock predictor response for DevRel draft scoring."""
    return json.dumps({
        "predicted_score": 78,
        "reasoning": "Similar API Design tutorials for backend developers averaged 78/100. Strong topic-format-audience alignment with high code-to-text ratio.",
        "suggestions": [
            "Add a runnable code example in the first 200 words to hook developers.",
            "Include a curl command or SDK snippet for quick-start adoption.",
            "Optimize for 'API authentication tutorial' keywords to improve search rank.",
        ],
        "confidence": "high",
        "comparable_count": 12,
        "code_quality_feedback": "Good code-to-text ratio. Consider adding error handling examples.",
        "code_to_text_ratio": 0.25,
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
