"""
LLM client for ContentPulse.
Supports Google Antigravity SDK (Gemini), Hugging Face Serverless (Qwen2.5-VL), and mock mode.
"""

import os
import json
import logging
import asyncio
from typing import Any, Type, TypeVar, Optional

from pydantic import BaseModel

try:
    from google.antigravity import Agent, LocalAgentConfig
    ANTIGRAVITY_AVAILABLE = True
except ImportError:
    ANTIGRAVITY_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from config import MOCK_LLM, GOOGLE_API_KEY, LLM_MODEL, LOGS_DIR

# Configure logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "llm_client.log"))
logger.setLevel(logging.INFO)

# LLM Provider configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
HF_TOKEN = os.getenv("HF_TOKEN", "")

# Initialize Hugging Face OpenAI client if token provided
hf_client = None
if HF_TOKEN and OPENAI_AVAILABLE:
    try:
        hf_client = OpenAI(
            base_url="https://api-inference.huggingface.co/v1/",
            api_key=HF_TOKEN,
        )
        logger.info("✓ Hugging Face Serverless client initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize Hugging Face client: {e}")

T = TypeVar("T", bound=BaseModel)


def _mock_analyzer_response() -> str:
    """Generate mock analyzer response with 6 insights."""
    insights: dict[str, Any] = {
        "insights": [
            "AI/ML content drives 40% higher engagement than the average topic.",
            "Blog posts outperform video in conversion rate by 2.3x.",
            "Developer audience shows strongest engagement with technical deep-dives.",
            "Content published in Q1 sees 25% more views than Q4.",
            "Short-form content (<500 words) has above-average search ranking.",
            "Case studies have the highest conversion rate across all formats.",
        ]
    }
    return json.dumps(insights)


def _mock_predictor_response() -> str:
    """Generate mock predictor response."""
    prediction: dict[str, Any] = {
        "predicted_score": 78,
        "reasoning": "Similar AI/ML blog posts for developers averaged 78/100. Strong topic-format-audience alignment.",
        "suggestions": [
            "Add a concrete code example in the first 200 words.",
            "Include benchmark comparisons to boost authority.",
            "Optimize for 'AI engineering' keywords to improve search rank.",
        ],
        "confidence": "high",
        "comparable_count": 12,
    }
    return json.dumps(prediction)


def _mock_generic_response() -> str:
    """Generate generic mock response."""
    response: dict[str, Any] = {
        "status": "mock",
        "message": "Mock LLM response - MOCK_LLM is enabled.",
        "data": None,
    }
    return json.dumps(response)


async def _call_gemini_antigravity(
    system_prompt: str,
    user_prompt: str,
    response_schema: Optional[Type[T]] = None,
    max_tokens: int = 500,
) -> str:
    """Execute async call via Google Antigravity SDK."""
    if not ANTIGRAVITY_AVAILABLE:
        raise ImportError("google.antigravity package not available")

    try:
        config = LocalAgentConfig(
            model=LLM_MODEL,
            system_instructions=system_prompt,
            response_schema=response_schema,
        )
        async with Agent(config=config) as agent:
            response = await agent.chat(user_prompt)
            
            if response_schema:
                # Get structured output as Pydantic model
                structured = await response.structured_output()
                if hasattr(structured, 'model_dump'):
                    return json.dumps(structured.model_dump())
                elif isinstance(structured, dict):
                    return json.dumps(structured)
                else:
                    return json.dumps(structured)
            
            # Get text response
            text = await response.text()
            return text

    except Exception as e:
        logger.error(f"Antigravity call failed: {e}", exc_info=True)
        raise e


def _call_huggingface_openai(
    system_prompt: str,
    user_prompt: str,
    response_schema: Optional[Type[T]] = None,
    max_tokens: int = 500,
) -> str:
    """Execute call via Hugging Face Serverless Inference API (Qwen2.5-VL-7B-Instruct)."""
    if not hf_client:
        raise RuntimeError("Hugging Face client not configured. Set HF_TOKEN environment variable.")

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = hf_client.chat.completions.create(
            model="Qwen/Qwen2.5-VL-7B-Instruct",
            messages=messages,
            temperature=0.3,
            max_tokens=max_tokens,
        )
        response_text = response.choices[0].message.content
        
        logger.info(f"✓ Hugging Face call successful. Tokens: {response.usage.completion_tokens}")
        return response_text

    except Exception as e:
        logger.error(f"Hugging Face call failed: {e}", exc_info=True)
        raise e


def call_llm(
    system_prompt: str,
    user_prompt: str,
    response_schema: Optional[Type[T]] = None,
    max_tokens: int = 500,
) -> str:
    """
    Call LLM with provider routing and fallback to mock mode.

    Args:
        system_prompt: System instruction for the LLM.
        user_prompt: User query/content.
        response_schema: Optional Pydantic schema for structured output validation.
        max_tokens: Maximum tokens in response (default 500).

    Returns:
        LLM response as JSON string. On error, returns JSON with error key.
    """
    # 1. Mock Mode Fallback
    if MOCK_LLM:
        logger.debug("Using mock LLM mode (MOCK_LLM=true)")
        system_lower = system_prompt.lower()
        if "analyzer" in system_lower or "analytics" in system_lower:
            return _mock_analyzer_response()
        elif "predictor" in system_lower or "predict" in system_lower:
            return _mock_predictor_response()
        else:
            return _mock_generic_response()

    # 2. Production Call Routing
    try:
        if LLM_PROVIDER == "huggingface":
            if not hf_client:
                raise RuntimeError("HF_TOKEN not set. Cannot use Hugging Face provider.")
            logger.info("→ Routing to Hugging Face Serverless API (Qwen2.5-VL-7B-Instruct)")
            result = _call_huggingface_openai(
                system_prompt, user_prompt, response_schema, max_tokens
            )
        else:
            if not ANTIGRAVITY_AVAILABLE:
                raise RuntimeError("google.antigravity not available. Install it with: pip install google-antigravity")
            logger.info(f"→ Routing to Google Antigravity SDK ({LLM_MODEL})")
            result = asyncio.run(
                _call_gemini_antigravity(
                    system_prompt, user_prompt, response_schema, max_tokens
                )
            )

        return result

    except Exception as e:
        error_msg: dict[str, Any] = {
            "error": "LLM call failed",
            "fallback": True,
            "details": str(e),
            "provider": LLM_PROVIDER,
        }
        logger.error(f"LLM call error ({LLM_PROVIDER}): {e}", exc_info=True)
        return json.dumps(error_msg)
