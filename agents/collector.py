"""
Collector agent for ContentPulse.
Loads, validates, and enriches raw content data.

OPTIMIZATION FEATURES:
- Streaming CSV reading (not loading entire file into memory)
- Batch processing with progress tracking
- Emit progress events for each batch
- Chunked data validation
"""

import logging
from datetime import date
from typing import Any, Iterator, Optional
import logging

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from agents.base_agent import BaseAgent
from config import DATA_PATH, LOGS_DIR, PERFORMANCE_WEIGHTS
from data.schema import RawContentRow

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "agents.log"))
logger.setLevel(logging.INFO)

# OPTIMIZATION: Streaming batch size
BATCH_SIZE = 100


class CollectorAgent(BaseAgent):
    """Collects, validates, and enriches content data with streaming support."""

    def __init__(self, data_path: str | None = None) -> None:
        """
        Initialize collector agent.

        Args:
            data_path: Path to CSV file (defaults to config.DATA_PATH).
        """
        super().__init__()
        self.data_path = data_path or str(DATA_PATH)
        logger.info(f"CollectorAgent initialized with data_path: {self.data_path}")

    def _stream_csv_batches(self) -> Iterator[pd.DataFrame]:
        """
        OPTIMIZATION: Stream CSV in batches instead of loading entire file.
        Yields batches of BATCH_SIZE rows to reduce memory footprint.
        """
        logger.info(f"Streaming CSV file: {self.data_path}")
        try:
            for chunk in pd.read_csv(self.data_path, chunksize=BATCH_SIZE):
                # Strip whitespace from string columns in this chunk
                string_cols = chunk.select_dtypes(include=["object", "string"]).columns
                for col in string_cols:
                    chunk[col] = chunk[col].apply(str.strip)
                
                yield chunk
                logger.debug(f"Yielded chunk of {len(chunk)} rows")
        except Exception as e:
            logger.error(f"Error streaming CSV: {e}", exc_info=True)
            raise

    def _validate_batch(self, batch_df: pd.DataFrame) -> tuple[list[dict], int]:
        """
        OPTIMIZATION: Validate a batch of rows.
        Returns: (valid_rows_list, dropped_count)
        """
        valid_rows = []
        dropped_rows = 0

        for idx, row in batch_df.iterrows():
            try:
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
                logger.debug(f"Row validation failed: {e}")

        return valid_rows, dropped_rows

    def run(self) -> dict[str, Any]:
        """
        Load, validate, and enrich content data using streaming.
        
        OPTIMIZATION: Process in batches to reduce memory usage and enable
        progress tracking without waiting for entire file to be read.

        Returns:
            Dictionary with keys:
            - dataframe: Enriched DataFrame
            - total_rows: Total rows in CSV
            - valid_rows: Valid rows after validation
            - dropped_rows: Rows dropped due to validation errors
        """
        logger.info(f"Starting streaming collection from {self.data_path}")
        
        valid_rows_all = []
        dropped_rows_total = 0
        total_rows_seen = 0
        batch_num = 0

        # Stream and process batches
        for batch in self._stream_csv_batches():
            batch_num += 1
            batch_size = len(batch)
            total_rows_seen += batch_size
            
            # Validate this batch
            valid_rows_batch, dropped_in_batch = self._validate_batch(batch)
            valid_rows_all.extend(valid_rows_batch)
            dropped_rows_total += dropped_in_batch
            
            # OPTIMIZATION: Emit progress event every batch
            logger.info(f"✓ Batch {batch_num}: Processed {batch_size} rows, "
                       f"valid: {len(valid_rows_batch)}, dropped: {dropped_in_batch}")
        
        logger.info(f"✓ Completed streaming: {total_rows_seen} total rows, "
                   f"{len(valid_rows_all)} valid, {dropped_rows_total} dropped")

        # Convert validated rows to DataFrame
        df = pd.DataFrame(valid_rows_all)
        
        if len(df) == 0:
            logger.warning("No valid rows after validation!")
            return {
                "dataframe": df,
                "total_rows": total_rows_seen,
                "valid_rows": 0,
                "dropped_rows": dropped_rows_total,
            }

        # Convert publish_date to datetime
        df["publish_date"] = pd.to_datetime(df["publish_date"])

        # ==================== DERIVE FIELDS (VECTORIZED) ====================
        # These operations are done on the complete dataframe for efficiency

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
        # OPTIMIZATION: Vectorized score computation

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
            "total_rows": total_rows_seen,
            "valid_rows": len(valid_rows_all),
            "dropped_rows": dropped_rows_total,
        }


__all__ = ["CollectorAgent"]
