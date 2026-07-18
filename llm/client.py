"""
LLM client for ContentPulse.
Provides unified interface to call LLM with mock fallback and error handling.
"""

import json
import logging
from typing import Any

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from config import MOCK_LLM, GOOGLE_API_KEY, LLM_MODEL, LOGS_DIR

# Configure logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "llm_client.log"))
logger.setLevel(logging.INFO)


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


def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 500) -> str:
    """
    Call LLM with fallback to mock mode.

    Args:
        system_prompt: System instruction for the LLM.
        user_prompt: User query/content.
        max_tokens: Maximum tokens in response (default 500).

    Returns:
        LLM response as JSON string. On error, returns JSON with error key.
    """
    # Mock mode
    if MOCK_LLM:
        system_lower = system_prompt.lower()
        if "analyzer" in system_lower or "analytics" in system_lower:
            return _mock_analyzer_response()
        elif "predictor" in system_lower or "predict" in system_lower:
            return _mock_predictor_response()
        else:
            return _mock_generic_response()

    # Real LLM mode
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(
            LLM_MODEL, system_instruction=system_prompt
        )
        generation_config = GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=0.3,
        )
        response = model.generate_content(
            user_prompt, generation_config=generation_config
        )
        return response.text

    except Exception as e:
        error_msg: dict[str, Any] = {
            "error": "LLM call failed",
            "fallback": True,
            "details": str(e),
        }
        logger.error(f"LLM call error: {e}")
        return json.dumps(error_msg)
