"""
Orchestrator module for ContentPulse.
Coordinates multi-agent pipeline execution.
"""

from orchestrator.pipeline import run_pipeline
from orchestrator.scorer import score_draft
from orchestrator.trace import ExecutionTrace

__all__ = ["ExecutionTrace", "run_pipeline", "score_draft"]
