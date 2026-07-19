"""
Collector agent for ContentPulse.
Loads, validates, and enriches raw content data.
"""

import logging
from datetime import date
from typing import Any

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from agents.base_agent import BaseAgent
from config import DATA_PATH, LOGS_DIR, PERFORMANCE_WEIGHTS
from data.schema import RawContentRow

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "agents.log"))
logger.setLevel(logging.INFO)


class CollectorAgent(BaseAgent):
    """Collects, validates, and enriches content data."""

    def __init__(self, data_path: str | None = None) -> None:
        """
        Initialize collector agent.

        Args:
            data_path: Path to CSV file (defaults to config.DATA_PATH).
        """
        super().__init__()
        self.data_path = data_path or str(DATA_PATH)
        logger.info(f"CollectorAgent initialized with data_path: {self.data_path}")

    def run(self) -> dict[str, Any]:
        """
        Load, validate, and enrich content data.

        Returns:
            Dictionary with keys:
            - dataframe: Enriched DataFrame
            - total_rows: Total rows in CSV
            - valid_rows: Valid rows after validation
            - dropped_rows: Rows dropped due to validation errors
        """
        # Load CSV
        logger.info(f"Loading data from {self.data_path}")
        df_raw = pd.read_csv(self.data_path)
        total_rows = len(df_raw)
        logger.info(f"Loaded {total_rows} rows from CSV")

        # Strip whitespace from string columns
        string_cols = df_raw.select_dtypes(include=["object", "string"]).columns
        for col in string_cols:
            df_raw[col] = df_raw[col].apply(str.strip)


        # Validate rows
        valid_rows = []
        dropped_rows = 0

        for idx, row in df_raw.iterrows():
            try:
                # Convert to dict and validate against schema
                row_dict = row.to_dict()
                # Handle NaN search_rank
                if pd.isna(row_dict.get("search_rank")):
                    row_dict["search_rank"] = None
                else:
                    row_dict["search_rank"] = int(row_dict["search_rank"])

                validated = RawContentRow(**row_dict)
                valid_rows.append(validated.model_dump())
            except Exception as e:
                dropped_rows += 1
                logger.debug(f"Row {idx} validation failed: {e}")

        logger.info(f"✓ Validated {len(valid_rows)} rows, dropped {dropped_rows}")

        # Convert to DataFrame
        df = pd.DataFrame(valid_rows)

        # Convert publish_date to datetime
        df["publish_date"] = pd.to_datetime(df["publish_date"])

        # ==================== DERIVE FIELDS (VECTORIZED) ====================

        # length_bucket
        df["length_bucket"] = pd.cut(
            df["word_count"],
            bins=[0, 500, 1500, 3000, float("inf")],
            labels=["short", "medium", "long", "evergreen"],
            right=False,
        )

        # publish_month (YYYY-MM)
        df["publish_month"] = df["publish_date"].dt.strftime("%Y-%m")

        # publish_quarter (YYYY-Qn)
        df["publish_quarter"] = df["publish_date"].dt.to_period("Q").astype(str)

        # days_since_publish (at least 1)
        df["days_since_publish"] = (date.today() - df["publish_date"].dt.date).apply(
            lambda x: x.days
        )
        df["days_since_publish"] = df["days_since_publish"].clip(lower=1)

        # views_per_day
        df["views_per_day"] = df["views"] / df["days_since_publish"]

        # ==================== COMPUTE PERFORMANCE SCORE ====================

        # Min-max normalize each metric
        scaler = MinMaxScaler(feature_range=(0, 1))

        # Normalize views
        views_norm = scaler.fit_transform(df[["views"]])[:, 0]

        # Normalize engagement_rate
        engagement_norm = scaler.fit_transform(df[["engagement_rate"]])[:, 0]

        # Normalize conversions
        conversions_norm = scaler.fit_transform(df[["conversions"]])[:, 0]

        # Search rank: fill NA with median, then invert (lower rank is better)
        search_rank_median = df["search_rank"].median()
        # If all search_rank are NaN, use a default
        if pd.isna(search_rank_median):
            search_rank_median = 50.0
        search_rank_filled = df["search_rank"].fillna(search_rank_median)
        
        # Normalize search_rank (0-1 scale)
        search_rank_norm_raw = scaler.fit_transform(
            search_rank_filled.values.reshape(-1, 1)
        )[:, 0]
        # Invert: lower rank is better, so higher normalized value
        rank_norm = 1.0 - search_rank_norm_raw

        # Normalize github_stars_growth
        github_default = df["github_stars_growth"].median()
        if pd.isna(github_default):
            github_default = 0.0
        github_filled = df["github_stars_growth"].fillna(github_default)
        github_norm = scaler.fit_transform(github_filled.values.reshape(-1, 1))[:, 0]

        # Weighted sum (includes DevRel github_stars_growth metric)
        performance_score = (
            PERFORMANCE_WEIGHTS["views"] * views_norm
            + PERFORMANCE_WEIGHTS["engagement_rate"] * engagement_norm
            + PERFORMANCE_WEIGHTS["conversions"] * conversions_norm
            + PERFORMANCE_WEIGHTS["search_rank"] * rank_norm
            + PERFORMANCE_WEIGHTS["github_stars_growth"] * github_norm
        ) * 100

        df["performance_score"] = performance_score.round(1)

        # ==================== SORT AND RETURN ====================

        # Sort by publish_date descending
        df = df.sort_values("publish_date", ascending=False).reset_index(drop=True)

        logger.info(
            f"✓ Enriched data with performance_score (range: {df['performance_score'].min():.1f} - {df['performance_score'].max():.1f})"
        )

        return {
            "dataframe": df,
            "total_rows": total_rows,
            "valid_rows": len(valid_rows),
            "dropped_rows": dropped_rows,
        }


__all__ = ["CollectorAgent"]
