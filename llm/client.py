"""LLM client supporting Google Antigravity SDK and Hugging Face."""
import os, json, logging, asyncio
from typing import Any, Type, TypeVar
from pydantic import BaseModel
from openai import OpenAI
from google.antigravity import Agent, LocalAgentConfig
from config import MOCK_LLM, LLM_PROVIDER, LLM_MODEL, GOOGLE_API_KEY, HF_TOKEN, LOGS_DIR

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "llm_client.log"))
logger.setLevel(logging.INFO)

T = TypeVar("T", bound=BaseModel)
hf_client = OpenAI(base_url="https://api-inference.huggingface.co/v1/", api_key=HF_TOKEN)

def _mock_analyzer_response() -> str:
    return json.dumps({"insights": [
        "API Design tutorials drive 45% higher developer signups than blog posts.",
        "Code examples with runnable snippets have 3x engagement rate.",
        "Backend developers show strongest conversion to API signups.",
        "Content published after major releases sees 60% more views.",
        "Tutorials under 1500 words have the highest completion rate.",
        "OAuth and Authentication guides rank highest in search."
    ]})

def _mock_predictor_response() -> str:
    return json.dumps({
        "predicted_score": 78,
        "reasoning": "Similar API Design tutorials for backend developers averaged 78/100.",
        "suggestions": ["Add runnable code in first 200 words", "Include curl command", "Optimize for API keywords"],
        "confidence": "high", "comparable_count": 12,
        "code_quality_feedback": "Good code ratio. Add error handling examples.",
        "code_to_text_ratio": 0.25
    })

def _mock_generic_response() -> str:
    return json.dumps({"status": "mock", "message": "Mock LLM response"})

async def _call_gemini_async(system_prompt: str, user_prompt: str, response_schema: Type[T] | None = None, max_tokens: int = 500) -> Any:
    config = LocalAgentConfig(model=LLM_MODEL, system_instructions=system_prompt, response_schema=response_schema)
    async with Agent(config=config) as agent:
        response = await agent.chat(user_prompt)
        return await response.structured_output() if response_schema else await response.text()

def _call_huggingface(system_prompt: str, user_prompt: str, response_schema: Type[T] | None = None, max_tokens: int = 500) -> Any:
    response = hf_client.chat.completions.create(
        model="Qwen/Qwen2.5-VL-7B-Instruct",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        temperature=0.3, max_tokens=max_tokens
    )
    text = response.choices[0].message.content
    return json.loads(text) if response_schema else text

def call_llm(system_prompt: str, user_prompt: str, response_schema: Type[T] | None = None, max_tokens: int = 500) -> Any:
    if MOCK_LLM:
        system_lower = system_prompt.lower()
        mock_str = _mock_analyzer_response() if "analyzer" in system_lower else (_mock_predictor_response() if "predictor" in system_lower else _mock_generic_response())
        return response_schema(**json.loads(mock_str)) if response_schema else mock_str

    try:
        if LLM_PROVIDER == "huggingface":
            result = _call_huggingface(system_prompt, user_prompt, response_schema, max_tokens)
        else:
            result = asyncio.run(_call_gemini_async(system_prompt, user_prompt, response_schema, max_tokens))
        return response_schema(**result) if (response_schema and isinstance(result, dict)) else result
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        if response_schema: raise
        return json.dumps({"error": "LLM call failed", "details": str(e)})
