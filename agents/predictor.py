"""
Predictor agent for ContentPulse.
Predicts content performance based on comparable historical data.
"""

import json
import logging
from typing import Any

import pandas as pd

from agents.base_agent import BaseAgent
from data.schema import PredictorInput, PredictorOutput
from llm import call_llm

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler("logs/agents.log"))
logger.setLevel(logging.INFO)


class PredictorAgent(BaseAgent):
    """Predicts content performance based on comparable historical data."""

    def __init__(self) -> None:
        """Initialize predictor agent."""
        super().__init__()

    def run(
        self,
        dataframe: pd.DataFrame | None = None,
        title: str | None = None,
        topic: str | None = None,
        format: str | None = None,
        audience_segment: str | None = None,
        word_count: int | None = None,
    ) -> PredictorOutput:
        """
        Predict content performance.

        Args:
            dataframe: Historical content data.
            title: Content title.
            topic: Content topic.
            format: Content format.
            audience_segment: Target audience.
            word_count: Content length.

        Returns:
            PredictorOutput with predicted score and suggestions.
        """
        if dataframe is None or dataframe.empty:
            raise ValueError("dataframe is required and cannot be empty")

        # ==================== STEP 1: VALIDATE INPUT ====================

        validated = PredictorInput(
            title=title or "Untitled",
            topic=topic or "AI/ML",
            format=format or "blog",
            audience_segment=audience_segment or "developers",
            word_count=word_count or 1500,
        )
        logger.info(
            f"Predicting for: {validated.topic}/{validated.format}/{validated.audience_segment}"
        )

        # ==================== STEP 2: FUZZY MATCHING ====================

        # Try: topic + format + audience
        subset = dataframe[
            (dataframe["topic"] == validated.topic)
            & (dataframe["format"] == validated.format)
            & (dataframe["audience_segment"] == validated.audience_segment)
        ]

        if len(subset) < 3:
            logger.debug(
                f"Only {len(subset)} rows with topic+format+audience, relaxing to topic+format"
            )
            subset = dataframe[
                (dataframe["topic"] == validated.topic)
                & (dataframe["format"] == validated.format)
            ]

        if len(subset) < 3:
            logger.debug(
                f"Only {len(subset)} rows with topic+format, relaxing to topic only"
            )
            subset = dataframe[dataframe["topic"] == validated.topic]

        logger.info(f"Found {len(subset)} comparable rows")

        # If still < 3: extreme fallback
        if len(subset) < 3:
            logger.warning(f"Only {len(subset)} comparable rows, using extreme fallback")
            return PredictorOutput(
                predicted_score=50,
                reasoning="Insufficient comparable data. Recommend publishing and monitoring performance.",
                suggestions=[
                    "Publish and monitor performance closely",
                    "Compare with similar topics in your niche",
                    "A/B test headlines and opening hooks",
                ],
                confidence="low",
                comparable_count=len(subset),
            )

        # ==================== STEP 3: BUILD SUMMARY ====================

        summary_parts = [
            f"Comparable content: {len(subset)} items",
            f"Performance score: mean={subset['performance_score'].mean():.1f}, "
            f"std={subset['performance_score'].std():.1f}, "
            f"min={subset['performance_score'].min():.1f}, "
            f"max={subset['performance_score'].max():.1f}, "
            f"median={subset['performance_score'].median():.1f}",
            f"Average views: {subset['views'].mean():.0f}",
            f"Average engagement: {subset['engagement_rate'].mean():.2%}",
            f"Average word count: {subset['word_count'].mean():.0f}",
        ]

        # Best format within subset
        best_format = subset.groupby("format")["performance_score"].mean().idxmax()
        summary_parts.append(f"Best format in subset: {best_format}")

        summary = "\n".join(summary_parts)
        logger.debug(f"Summary:\n{summary}")

        # ==================== STEP 4: LLM CALL ====================

        system_prompt = (
            'You are a content predictor expert. Return JSON: '
            '{"predicted_score": <0-100>, "reasoning": "<1 sentence>", '
            '"suggestions": ["<s1>", "<s2>", "<s3>"], '
            '"confidence": "<high|medium|low>", "comparable_count": <N>}'
        )
        user_prompt = (
            f"Proposed content:\n"
            f"Title: {validated.title}\n"
            f"Topic: {validated.topic}\n"
            f"Format: {validated.format}\n"
            f"Audience: {validated.audience_segment}\n"
            f"Word count: {validated.word_count}\n\n"
            f"Comparable historical data:\n{summary}\n\n"
            f"Predict performance score (0-100), confidence level, and 3 specific suggestions."
        )

        try:
            response_text = call_llm(system_prompt, user_prompt, max_tokens=400)
            response_obj = json.loads(response_text)

            # Validate required fields
            predicted_score = int(response_obj.get("predicted_score", 50))
            predicted_score = max(0, min(100, predicted_score))  # Clamp to 0-100

            reasoning = response_obj.get("reasoning", "")
            suggestions = response_obj.get("suggestions", [])
            confidence = response_obj.get("confidence", "medium")
            comparable_count = response_obj.get("comparable_count", len(subset))

            # Validate suggestions length
            if len(suggestions) != 3:
                logger.warning(
                    f"LLM returned {len(suggestions)} suggestions, expected 3, using fallback"
                )
                raise ValueError("Invalid suggestions length")

            logger.info(
                f"✓ LLM predicted score={predicted_score}, confidence={confidence}"
            )

            return PredictorOutput(
                predicted_score=predicted_score,
                reasoning=reasoning,
                suggestions=suggestions,
                confidence=confidence,
                comparable_count=comparable_count,
            )

        except (json.JSONDecodeError, ValueError, KeyError, Exception) as e:
            logger.warning(f"LLM parsing failed: {e}, using statistical fallback")
            return self._statistical_fallback(subset)

    def _statistical_fallback(self, subset: pd.DataFrame) -> PredictorOutput:
        """Generate prediction using statistical fallback."""
        predicted_score = int(round(subset["performance_score"].median()))
        comparable_count = len(subset)

        # Confidence based on sample size
        if comparable_count >= 20:
            confidence = "high"
        elif comparable_count >= 10:
            confidence = "medium"
        else:
            confidence = "low"

        # Suggestions from top format
        best_format = subset.groupby("format")["performance_score"].mean().idxmax()
        best_format_score = (
            subset[subset["format"] == best_format]["performance_score"].mean()
        )
        avg_engagement = subset["engagement_rate"].mean()
        avg_views = subset["views"].mean()

        suggestions = [
            f"Use {best_format} format for highest average performance ({best_format_score:.0f}).",
            f"Target average engagement rate of {avg_engagement:.1%} based on comparable content.",
            f"Aim for {avg_views:.0f} average views based on similar content performance.",
        ]

        reasoning = (
            f"Based on {comparable_count} comparable pieces. "
            f"Median performance score is {predicted_score}."
        )

        logger.info(
            f"✓ Statistical fallback: score={predicted_score}, confidence={confidence}"
        )

        return PredictorOutput(
            predicted_score=predicted_score,
            reasoning=reasoning,
            suggestions=suggestions,
            confidence=confidence,
            comparable_count=comparable_count,
        )


__all__ = ["PredictorAgent"]
