"""
Scorer for ContentPulse.
Predicts performance of draft content.
"""

import json
import logging
import sys
from typing import Any

from agents import CollectorAgent, PredictorAgent
from config import DATA_PATH, LOGS_DIR
from orchestrator.trace import ExecutionTrace

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "orchestrator.log"))
logger.setLevel(logging.INFO)


def score_draft(
    title: str,
    topic: str,
    fmt: str,
    audience_segment: str,
    word_count: int,
    data_path: str | None = None,
    draft_markdown: str | None = None,
) -> dict[str, Any]:
    """
    Score a draft piece of content.

    Args:
        title: Content title.
        topic: Content topic.
        fmt: Content format.
        audience_segment: Target audience.
        word_count: Content length.
        data_path: Path to historical data (defaults to config.DATA_PATH).
        draft_markdown: Optional markdown draft for code analysis.

    Returns:
        Dictionary with prediction and trace.
    """
    trace = ExecutionTrace()
    trace.start()

    logger.info("=" * 60)
    logger.info("SCORING DRAFT CONTENT")
    logger.info("=" * 60)

    # ==================== COLLECTOR ====================
    logger.info("Loading historical data...")
    collector = CollectorAgent(data_path=data_path or str(DATA_PATH))
    collector_result, collector_duration, collector_status = collector.execute()

    trace.add(
        agent="CollectorAgent",
        input_summary=f"CSV: {data_path or DATA_PATH}",
        output_summary=f"{collector_result['valid_rows']} rows loaded",
        duration_seconds=collector_duration,
        status=collector_status,
    )

    if collector_status != "success":
        logger.error("Scoring failed at Collector stage")
        return {
            "error": "Collector failed",
            "trace": trace.to_dict(),
        }

    dataframe = collector_result["dataframe"]

    # ==================== PREDICTOR ====================
    logger.info("Predicting performance...")
    predictor = PredictorAgent()
    prediction, predictor_duration, predictor_status = predictor.execute(
        dataframe=dataframe,
        title=title,
        topic=topic,
        format=fmt,
        audience_segment=audience_segment,
        word_count=word_count,
        draft_markdown=draft_markdown,
    )

    trace.add(
        agent="PredictorAgent",
        input_summary=f"{title} ({topic}/{fmt}/{audience_segment})",
        output_summary=f"Score: {prediction.predicted_score}, Comparable: {prediction.comparable_count}",
        duration_seconds=predictor_duration,
        status=predictor_status,
    )

    if predictor_status != "success":
        logger.error("Scoring failed at Predictor stage")
        return {
            "error": "Predictor failed",
            "trace": trace.to_dict(),
        }

    logger.info("=" * 60)
    logger.info("SCORING COMPLETE")
    logger.info(f"Total duration: {trace.total_duration:.2f}s")
    logger.info("=" * 60)

    return {
        "prediction": prediction.model_dump(),
        "trace": trace.to_dict(),
    }


if __name__ == "__main__":
    # Parse command-line arguments: title topic format word_count
    if len(sys.argv) < 5:
        print(
            "Usage: python3 -m orchestrator.scorer <title> <topic> <format> <word_count> [audience] [data_path]"
        )
        sys.exit(1)

    title = sys.argv[1]
    topic = sys.argv[2]
    fmt = sys.argv[3]
    word_count = int(sys.argv[4])
    audience = sys.argv[5] if len(sys.argv) > 5 else "developers"
    data_path = sys.argv[6] if len(sys.argv) > 6 else None
    draft_markdown = sys.argv[7] if len(sys.argv) > 7 else None

    result = score_draft(
        title=title,
        topic=topic,
        fmt=fmt,
        audience_segment=audience,
        word_count=word_count,
        data_path=data_path,
        draft_markdown=draft_markdown,
    )
    print(json.dumps(result, indent=2, default=str))
