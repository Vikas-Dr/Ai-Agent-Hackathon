"""
Analyzer agent for ContentPulse — DevRel Specialization.
Analyzes developer content performance by topic, format, and specialization.
Focuses on API conversions, GitHub engagement, and keyword rankings.
Uses Pydantic structured output validation.
"""

import logging
from typing import Any

import pandas as pd

import json
from agents.base_agent import BaseAgent
from data.schema import (
    AnalyzerOutput,
    AudienceBreakdown,
    FormatBreakdown,
    LengthAnalysis,
    PeriodTrend,
    TopicBreakdown,
)
from llm import call_llm

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler("logs/agents.log"))
logger.setLevel(logging.INFO)


class AnalyzerAgent(BaseAgent):
    """Analyzes developer content performance across topics, formats, and specializations."""

    def __init__(self) -> None:
        """Initialize DevRel analyzer agent."""
        super().__init__()

    def run(self, dataframe: pd.DataFrame | None = None) -> AnalyzerOutput:
        """
        Analyze developer content performance.
        
        Metrics analyzed:
        - Views: Developer article pageviews
        - Engagement: GitHub star/fork interaction rate
        - Conversions: API key creations or console signups (PRIMARY)
        - Keywords: Developer keyword rankings

        Args:
            dataframe: Input DataFrame from CollectorAgent with DevRel metrics.

        Returns:
            AnalyzerOutput with insights focused on developer conversion patterns.
        """
        if dataframe is None or dataframe.empty:
            raise ValueError("dataframe is required and cannot be empty")

        # Topic analysis
        topic_agg = (
            dataframe.groupby("topic")["performance_score"]
            .agg(["mean", "count"])
            .reset_index()
            .rename(columns={"mean": "avg_score", "count": "count"})
            .sort_values("avg_score", ascending=False)
        )
        topic_agg["avg_score"] = topic_agg["avg_score"].round(1)
        top_topics = [
            TopicBreakdown(
                topic=row["topic"],
                avg_score=row["avg_score"],
                count=int(row["count"]),
            )
            for _, row in topic_agg.iterrows()
        ]

        # Format analysis
        format_agg = (
            dataframe.groupby("format")["performance_score"]
            .agg(["mean", "count"])
            .reset_index()
            .rename(columns={"mean": "avg_score", "count": "count"})
            .sort_values("avg_score", ascending=False)
        )
        format_agg["avg_score"] = format_agg["avg_score"].round(1)
        top_formats = [
            FormatBreakdown(
                format=row["format"],
                avg_score=row["avg_score"],
                count=int(row["count"]),
            )
            for _, row in format_agg.iterrows()
        ]

        # Audience analysis
        audience_agg = (
            dataframe.groupby("audience_segment")["performance_score"]
            .agg(["mean", "count"])
            .reset_index()
            .rename(columns={"mean": "avg_score", "count": "count"})
            .sort_values("avg_score", ascending=False)
        )
        audience_agg["avg_score"] = audience_agg["avg_score"].round(1)
        audience_analysis = [
            AudienceBreakdown(
                segment=row["audience_segment"],
                avg_score=row["avg_score"],
                count=int(row["count"]),
            )
            for _, row in audience_agg.iterrows()
        ]

        # Period trends
        period_agg = (
            dataframe.groupby("publish_quarter")
            .agg(
                avg_views=("views", "mean"),
                avg_engagement=("engagement_rate", "mean"),
            )
            .reset_index()
            .sort_values("publish_quarter", ascending=True)
        )
        period_agg["avg_views"] = period_agg["avg_views"].astype(int)
        period_agg["avg_engagement"] = period_agg["avg_engagement"].round(4)
        period_trends = [
            PeriodTrend(
                period=row["publish_quarter"],
                avg_views=int(row["avg_views"]),
                avg_engagement=float(row["avg_engagement"]),
            )
            for _, row in period_agg.iterrows()
        ]

        # Length bucket analysis
        length_order = ["short", "medium", "long", "evergreen"]
        length_agg = (
            dataframe.groupby("length_bucket")["performance_score"]
            .agg(["mean", "count"])
            .reset_index()
            .rename(columns={"mean": "avg_score", "count": "count"})
        )
        # Reorder by bucket
        length_agg["length_bucket"] = pd.Categorical(
            length_agg["length_bucket"], categories=length_order, ordered=True
        )
        length_agg = length_agg.sort_values("length_bucket")
        length_agg["avg_score"] = length_agg["avg_score"].round(1)
        length_analysis = [
            LengthAnalysis(
                bucket=row["length_bucket"],
                avg_score=row["avg_score"],
                count=int(row["count"]),
            )
            for _, row in length_agg.iterrows()
        ]

        logger.info(f"✓ Computed aggregations: {len(top_topics)} topics, {len(top_formats)} formats")

        # ==================== COMPUTE DEVREL METRICS ====================
        
        devrel_metrics = {
            "total_github_stars": dataframe.get("github_stars_growth", pd.Series([0])).sum() if "github_stars_growth" in dataframe.columns else 0,
            "avg_github_stars": dataframe.get("github_stars_growth", pd.Series([0])).mean() if "github_stars_growth" in dataframe.columns else 0,
            "total_api_signups": int(dataframe["conversions"].sum()),
            "avg_api_signups": round(dataframe["conversions"].mean(), 2),
            "avg_code_ratio": 0.35,
        }
        logger.info(f"✓ DevRel metrics: GitHub stars={devrel_metrics['total_github_stars']}, API signups={devrel_metrics['total_api_signups']}")

        # ==================== STEP 2: BUILD SUMMARY ====================

        summary_lines = [
            "AGGREGATED PERFORMANCE DATA",
            "",
            "Topic Performance:",
        ]
        for item in top_topics:
            summary_lines.append(
                f"  - {item.topic}: avg_score={item.avg_score}, count={item.count}"
            )

        summary_lines.append("\nFormat Performance:")
        for item in top_formats:
            summary_lines.append(
                f"  - {item.format}: avg_score={item.avg_score}, count={item.count}"
            )

        summary_lines.append("\nAudience Segment:")
        for item in audience_analysis:
            summary_lines.append(
                f"  - {item.segment}: avg_score={item.avg_score}, count={item.count}"
            )

        summary_lines.append("\nQuarterly Trends:")
        for item in period_trends:
            summary_lines.append(
                f"  - {item.period}: avg_views={item.avg_views}, avg_engagement={item.avg_engagement}"
            )

        summary_lines.append("\nLength Bucket:")
        for item in length_analysis:
            summary_lines.append(
                f"  - {item.bucket}: avg_score={item.avg_score}, count={item.count}"
            )

        summary = "\n".join(summary_lines)
        logger.debug(f"Summary:\n{summary}")

        # ==================== STEP 3: LLM CALL ====================

        system_prompt = (
            "You are a DevRel strategist analyzing developer content performance. "
            "Return JSON insights focused on: (1) API signups/conversions, (2) GitHub engagement, "
            "(3) developer keyword rankings, (4) topic-format alignment for developers. "
            "Each insight is one sentence, grounded in data, and actionable for developer relations decisions."
        )
        user_prompt = (
            f"DevRel Performance Data:\n{summary}\n\n"
            f"DevRel Metrics:\n"
            f"- Total GitHub stars: {devrel_metrics['total_github_stars']}\n"
            f"- Avg GitHub stars per item: {devrel_metrics['avg_github_stars']:.1f}\n"
            f"- Total API signups: {devrel_metrics['total_api_signups']}\n"
            f"- Avg API signups: {devrel_metrics['avg_api_signups']}\n"
            f"- Avg code ratio: {devrel_metrics['avg_code_ratio']:.1%}\n\n"
            "Return 4-6 insights about developer content performance patterns. "
            "Prioritize conversion metrics (API signups), developer specialization engagement, "
            "and topic coverage gaps that matter to frontend/backend/devops/architect audiences."
        )

        try:
            response_text = call_llm(system_prompt, user_prompt)
            response_obj = json.loads(response_text) if isinstance(response_text, str) else response_text
            insights = response_obj.get("insights", []) if isinstance(response_obj, dict) else []
            if not insights:
                insights = self._generate_fallback_insights(dataframe)
        except Exception as e:
            logger.warning(f"LLM failed: {e}, using fallback insights")
            insights = self._generate_fallback_insights(dataframe)

        return AnalyzerOutput(
            insights=insights,
            top_topics=top_topics,
            top_formats=top_formats,
            audience_analysis=audience_analysis,
            period_trends=period_trends,
            length_analysis=length_analysis,
            devrel_metrics=devrel_metrics,
        )


    def _generate_fallback_insights(self, dataframe: pd.DataFrame) -> list[str]:
        """Generate deterministic fallback insights."""
        insights = []

        # Best topic
        best_topic = (
            dataframe.groupby("topic")["performance_score"].mean().idxmax()
        )
        best_topic_score = dataframe[dataframe["topic"] == best_topic][
            "performance_score"
        ].mean()
        insights.append(
            f"Top-performing topic: {best_topic} with average score {best_topic_score:.1f}."
        )

        # Worst topic
        worst_topic = (
            dataframe.groupby("topic")["performance_score"].mean().idxmin()
        )
        worst_topic_score = dataframe[dataframe["topic"] == worst_topic][
            "performance_score"
        ].mean()
        insights.append(
            f"Underperforming topic: {worst_topic} with average score {worst_topic_score:.1f}."
        )

        # Best format
        best_format = (
            dataframe.groupby("format")["performance_score"].mean().idxmax()
        )
        best_format_score = dataframe[dataframe["format"] == best_format][
            "performance_score"
        ].mean()
        insights.append(
            f"Best-performing format: {best_format} with average score {best_format_score:.1f}."
        )

        # Best audience
        best_audience = (
            dataframe.groupby("audience_segment")["performance_score"]
            .mean()
            .idxmax()
        )
        best_audience_score = dataframe[
            dataframe["audience_segment"] == best_audience
        ]["performance_score"].mean()
        insights.append(
            f"Most engaged audience: {best_audience} with average score {best_audience_score:.1f}."
        )

        # Best length bucket
        best_length = (
            dataframe.groupby("length_bucket")["performance_score"].mean().idxmax()
        )
        best_length_score = dataframe[dataframe["length_bucket"] == best_length][
            "performance_score"
        ].mean()
        insights.append(
            f"Best content length: {best_length}-form with average score {best_length_score:.1f}."
        )

        # Conversion rate
        total_conversions = dataframe["conversions"].sum()
        total_views = dataframe["views"].sum()
        conversion_rate = total_conversions / max(total_views, 1)
        insights.append(
            f"Overall conversion rate: {conversion_rate:.2%} across all content."
        )

        logger.info(f"✓ Generated {len(insights)} fallback insights")
        return insights


__all__ = ["AnalyzerAgent"]
