"""
LLM client module for ContentPulse.
Provides a unified interface to call LLM with fallback to mock mode.
"""

from llm.client import call_llm

__all__ = ["call_llm"]
