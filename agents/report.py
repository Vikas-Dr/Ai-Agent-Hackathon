"""
Report agent for ContentPulse.
Generates strategic editorial recommendations.
"""

import logging
from datetime import date

from agents.base_agent import BaseAgent
from data.schema import (
    AnalyzerOutput,
    ContinueItem,
    CreateNextItem,
    ReportOutput,
    StopItem,
    StrategistOutput,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler("logs/agents.log"))
logger.setLevel(logging.INFO)


class ReportAgent(BaseAgent):
    """Generates strategic editorial recommendations."""

    def __init__(self) -> None:
        """Initialize report agent."""
        super().__init__()

    def run(
        self,
        analysis: AnalyzerOutput | None = None,
        gaps: StrategistOutput | None = None,
    ) -> ReportOutput:
        """
        Generate strategic editorial report.

        Args:
            analysis: AnalyzerOutput from AnalyzerAgent.
            gaps: StrategistOutput from StrategistAgent.

        Returns:
            ReportOutput with recommendations.
        """
        if analysis is None or gaps is None:
            raise ValueError("analysis and gaps are required")

        # ==================== BUILD CONTEXT ====================

        # Topic scores and best format
        topic_scores = {item.topic: item.avg_score for item in analysis.top_topics}
        best_format = (
            analysis.top_formats[0].format if analysis.top_formats else "blog"
        )

        logger.info(f"Best format: {best_format}")

        # ==================== CONTINUE ITEMS ====================

        continue_items: list[ContinueItem] = []
        for topic in topic_scores:
            score = topic_scores[topic]
            if score >= 60:
                continue_items.append(
                    ContinueItem(
                        topic=topic,
                        format=best_format,
                        reason=f"Strong performance (score {score:.1f}). Continue investing in this topic.",
                    )
                )
                logger.info(f"Continue: {topic} (score {score:.1f})")

        # ==================== STOP ITEMS ====================

        stop_items: list[StopItem] = []
        for topic in topic_scores:
            score = topic_scores[topic]
            if score < 35:
                stop_items.append(
                    StopItem(
                        topic=topic,
                        format=best_format,
                        reason=f"Underperforming (score {score:.1f}). Consider pausing production.",
                    )
                )
                logger.info(f"Stop: {topic} (score {score:.1f})")

        # ==================== CREATE NEXT ITEMS ====================

        create_next: list[CreateNextItem] = []
        for gap, reason in zip(gaps.gaps, gaps.reasons):
            create_next.append(
                CreateNextItem(
                    topic=gap,
                    format="tutorial",
                    target_audience="developers",
                    reasoning=reason,
                )
            )
            logger.info(f"Create: {gap} — {reason}")

        # ==================== SUMMARY ====================

        top_continue = (
            continue_items[0].topic if continue_items else "high-performers"
        )
        summary = (
            f"DevRel recommendation: Focus on {top_continue} and high-engagement developer content. "
            f"Pause {len(stop_items)} underperforming streams. "
            f"Launch {len(create_next)} new developer guides/tutorials to drive SDK and framework adoption."
        )
        logger.info(f"Summary: {summary}")

        # ==================== RETURN REPORT ====================

        report = ReportOutput(
            report_date=date.today(),
            period="Last 12 months",
            summary=summary,
            continue_items=continue_items,
            stop_items=stop_items,
            create_next=create_next,
        )

        logger.info(f"✓ Generated report with {len(continue_items)} continue, {len(stop_items)} stop, {len(create_next)} create")

        return report


__all__ = ["ReportAgent"]
