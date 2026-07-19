"""
Strategist agent for ContentPulse — DevRel Specialization.
Identifies content gaps and opportunities for developer audience.
Focuses on emerging developer tools and framework coverage.
"""

import logging
from typing import Any

from agents.base_agent import BaseAgent
from data.schema import AnalyzerOutput, StrategistOutput

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler("logs/agents.log"))
logger.setLevel(logging.INFO)

# Emerging DevRel Topics: developer platforms/frameworks with coverage gaps
TRENDING_DEVREL_TOPICS = [
    "AI/ML APIs & SDKs",
    "Vector Databases",
    "Rust Web Frameworks",
    "GraphQL Subscriptions",
    "Observability Platforms",
    "API Rate Limiting Patterns",
]


class StrategistAgent(BaseAgent):
    """Identifies content gaps and strategic opportunities."""

    def __init__(self) -> None:
        """Initialize DevRel strategist agent."""
        super().__init__()

    def run(self, analysis: AnalyzerOutput | None = None) -> StrategistOutput:
        """
        Identify developer content gaps and opportunities.
        
        Detects:
        - Emerging technologies without coverage
        - Underperforming developer specializations
        - Framework/platform gaps that matter to APIs/DevOps/Security

        Args:
            analysis: AnalyzerOutput from AnalyzerAgent.

        Returns:
            StrategistOutput with gaps and reasons for developer relations.
        """
        if analysis is None:
            raise ValueError("analysis is required")

        gaps: list[str] = []
        reasons: list[str] = []

        # ==================== BUILD CONTEXT ====================

        # Covered topics from analysis
        covered_topics = {item.topic for item in analysis.top_topics}
        topic_scores = {item.topic: item.avg_score for item in analysis.top_topics}

        logger.info(f"Covered topics: {covered_topics}")

        # ==================== DETECT GAPS ====================

        # Gap 1: Trending topics not covered
        for trending in TRENDING_TOPICS:
            if trending not in covered_topics:
                gaps.append(trending)
                reasons.append(
                    f"Zero coverage of trending topic '{trending}' — first-mover opportunity"
                )
                logger.info(f"Gap: Trending topic not covered: {trending}")

        # Gap 2: Low-scoring topics
        for topic in covered_topics:
            score = topic_scores.get(topic, 0)
            if score < 40:
                gaps.append(topic)
                reasons.append(
                    f"Low average score ({score:.1f}) for topic '{topic}' — consider refreshing or reframing"
                )
                logger.info(f"Gap: Low-scoring topic: {topic} ({score:.1f})")

        # ==================== FALLBACK IF NO GAPS ====================

        if not gaps:
            gaps = ["No critical gaps detected"]
            reasons = [
                "Current content portfolio covers key topics with solid performance"
            ]
            logger.info("No critical gaps detected")

        logger.info(f"✓ Identified {len(gaps)} gaps")

        return StrategistOutput(gaps=gaps, reasons=reasons)


__all__ = ["StrategistAgent"]
