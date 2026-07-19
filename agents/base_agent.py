"""
Base agent class for ContentPulse.
All agents inherit from BaseAgent and implement the run() method.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any

from config import LOGS_DIR

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "agents.log"))
logger.setLevel(logging.INFO)


class BaseAgent(ABC):
    """Abstract base class for all ContentPulse agents."""

    def __init__(self, name: str | None = None) -> None:
        """
        Initialize base agent.

        Args:
            name: Agent name (defaults to class name).
        """
        self.name = name or self.__class__.__name__
        logger.info(f"Initialized {self.name}")

    @abstractmethod
    def run(self, **kwargs: Any) -> Any:
        """
        Execute agent logic. Must be implemented by subclasses.

        Args:
            **kwargs: Agent-specific arguments.

        Returns:
            Agent-specific result object.
        """
        pass

    def execute(self, **kwargs: Any) -> tuple[Any, float, str]:
        """
        Execute agent with error handling and timing.

        Args:
            **kwargs: Agent-specific arguments.

        Returns:
            Tuple of (result, duration_seconds, status).
            Status is "success" or "error".
        """
        start_time = time.time()
        status = "success"
        result = None

        try:
            result = self.run(**kwargs)
            logger.info(
                f"{self.name} completed successfully in {time.time() - start_time:.2f}s"
            )
        except Exception as e:
            status = "error"
            logger.error(f"{self.name} failed with error: {e}", exc_info=True)
            result = {"error": str(e)}

        duration_seconds = time.time() - start_time
        return result, duration_seconds, status


__all__ = ["BaseAgent"]
