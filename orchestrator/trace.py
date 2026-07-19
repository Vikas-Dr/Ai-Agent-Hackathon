"""
Execution trace for ContentPulse pipeline.
Records agent execution details and timing.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from data.schema import TraceEntry

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler("logs/orchestrator.log"))
logger.setLevel(logging.INFO)


class ExecutionTrace:
    """Records execution details for the entire pipeline."""

    def __init__(self) -> None:
        """Initialize execution trace."""
        self.entries: list[TraceEntry] = []
        self.start_time: datetime | None = None

    def start(self) -> None:
        """Reset and start trace."""
        self.entries = []
        self.start_time = datetime.now()
        logger.info("✓ Trace started")

    def add(
        self,
        agent: str,
        input_summary: str,
        output_summary: str,
        duration_seconds: float,
        status: str,
    ) -> None:
        """
        Add trace entry.

        Args:
            agent: Agent name.
            input_summary: Input description.
            output_summary: Output description.
            duration_seconds: Execution time.
            status: "success" or "error".
        """
        entry = TraceEntry(
            agent=agent,
            input_summary=input_summary,
            output_summary=output_summary,
            duration_seconds=duration_seconds,
            status=status,
        )
        self.entries.append(entry)
        logger.info(
            f"Trace: {agent} ({status}, {duration_seconds:.3f}s)"
        )

    @property
    def total_duration(self) -> float:
        """Total pipeline duration in seconds."""
        if not self.start_time:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """Convert trace to dictionary."""
        return {
            "entries": [e.model_dump() for e in self.entries],
            "total_duration_seconds": self.total_duration,
            "entry_count": len(self.entries),
            "timestamp": self.start_time.isoformat() if self.start_time else None,
        }

    def to_json(self) -> str:
        """Convert trace to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)

    def save(self, path: Path | str) -> None:
        """Save trace to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(self.to_json())
        logger.info(f"✓ Trace saved to {path}")


__all__ = ["ExecutionTrace"]
