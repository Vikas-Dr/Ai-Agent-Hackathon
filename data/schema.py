"""
Pydantic v2 data models for DevPulse.
Defines validated schema for developer content data, predictions, analysis, and reporting.
"""

from datetime import date, datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import re

from config import TOPICS, FORMATS, AUDIENCE_SEGMENTS

# ==================== LLM STRUCTURED OUTPUT ====================
class AnalyzerInsightsOutput(BaseModel):
    """Structured output from LLM for analyzer insights."""
    insights: list[str] = Field(..., min_length=4, max_length=6)


class PredictorStructuredOutput(BaseModel):
    """Structured output from LLM for predictor."""
    predicted_score: int = Field(..., ge=0, le=100)
    reasoning: str
    suggestions: list[str] = Field(..., min_length=3, max_length=3)
    confidence: str
    comparable_count: int = Field(..., ge=0)




# ==================== RAW DATA ====================
class RawContentRow(BaseModel):
    """Raw developer content row from CSV.
    
    Metrics mapping for DevPulse:
    - views: Developer documentation/article pageviews
    - engagement_rate: Social engagement (GitHub stars, tweets, shares) (0.0-1.0)
    - conversions: Developer signups, API key creations, or tool adoptions
    - search_rank: Developer SEO keyword ranking (1-100)
    - github_stars_growth: Growth rate of GitHub repository stars
    - audience_segment: Developer specialization (frontend|backend|devops|architects)
    """

    title: str = Field(..., min_length=1, max_length=200)
    url: str
    topic: str  # API Design, Authentication, Cloud Infrastructure, etc.
    format: str  # technical_blog, tutorial, code_example, documentation, etc.
    audience_segment: str  # frontend, backend, devops, architects
    word_count: int = Field(..., ge=100, le=20000)
    publish_date: date
    views: int = Field(..., ge=0, description="Developer documentation/article pageviews")
    engagement_rate: float = Field(..., ge=0.0, le=1.0, description="Social engagement rate (GitHub, social media)")
    avg_time_on_page: float = Field(..., ge=0, description="Time on page (seconds)")
    conversions: int = Field(..., ge=0, description="Developer signups, API key creations, or adoptions")
    search_rank: Optional[int] = Field(None, ge=1, le=100, description="Developer SEO keyword ranking")
    github_stars_growth: int = Field(default=0, ge=0)
    api_signups: int = Field(default=0, ge=0)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not re.match(r"^https?://", v):
            raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Validate topic against configured list."""
        if v not in TOPICS:
            raise ValueError(f"Topic must be one of {TOPICS}")
        return v

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate format against configured list."""
        if v not in FORMATS:
            raise ValueError(f"Format must be one of {FORMATS}")
        return v

    @field_validator("audience_segment")
    @classmethod
    def validate_audience(cls, v: str) -> str:
        """Validate audience segment against configured list."""
        if v not in AUDIENCE_SEGMENTS:
            raise ValueError(f"Audience segment must be one of {AUDIENCE_SEGMENTS}")
        return v

    @field_validator("publish_date")
    @classmethod
    def validate_publish_date(cls, v: date) -> date:
        """Ensure publish date is not in the future."""
        if v > date.today():
            raise ValueError("Publish date cannot be in the future")
        return v


# ==================== CLEANED DATA ====================
class CleanedContentRow(RawContentRow):
    """Cleaned and enriched content row with derived fields."""

    length_bucket: str = Field(default="")
    publish_month: str = Field(default="")
    publish_quarter: str = Field(default="")
    days_since_publish: int = Field(default=0)
    views_per_day: float = Field(default=0.0)
    performance_score: float = Field(default=0.0)
    code_to_text_ratio: float = Field(default=0.0, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def derive_fields(self) -> "CleanedContentRow":
        """Derive fields from publish_date and other values."""
        # Derive length_bucket
        if self.word_count < 500:
            self.length_bucket = "short"
        elif self.word_count < 1500:
            self.length_bucket = "medium"
        elif self.word_count < 3000:
            self.length_bucket = "long"
        else:
            self.length_bucket = "evergreen"

        # Derive publish_month (YYYY-MM)
        self.publish_month = self.publish_date.strftime("%Y-%m")

        # Derive publish_quarter (YYYY-Qn)
        quarter = (self.publish_date.month - 1) // 3 + 1
        self.publish_quarter = f"{self.publish_date.year}-Q{quarter}"

        # Derive days_since_publish
        self.days_since_publish = (date.today() - self.publish_date).days

        # Derive views_per_day
        if self.days_since_publish > 0:
            self.views_per_day = self.views / self.days_since_publish
        else:
            self.views_per_day = float(self.views)

        # Derive performance_score (0-100 scale using weights)
        # Placeholder: will be computed by orchestrator
        self.performance_score = 0.0

        return self


# ==================== PREDICTOR ====================
class PredictorInput(BaseModel):
    """Input for content performance predictor."""

    title: str = Field(..., min_length=1, max_length=200)
    topic: str
    format: str
    audience_segment: str
    word_count: int = Field(..., ge=100, le=20000)
    draft_markdown: str = Field(default="", max_length=50000)

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Validate topic against configured list."""
        if v not in TOPICS:
            raise ValueError(f"Topic must be one of {TOPICS}")
        return v

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate format against configured list."""
        if v not in FORMATS:
            raise ValueError(f"Format must be one of {FORMATS}")
        return v

    @field_validator("audience_segment")
    @classmethod
    def validate_audience(cls, v: str) -> str:
        """Validate audience segment against configured list."""
        if v not in AUDIENCE_SEGMENTS:
            raise ValueError(f"Audience segment must be one of {AUDIENCE_SEGMENTS}")
        return v


class PredictorOutput(BaseModel):
    """Output from content performance predictor."""

    predicted_score: int = Field(..., ge=0, le=100)
    reasoning: str
    suggestions: list[str] = Field(..., min_length=3, max_length=3)
    confidence: str
    comparable_count: int = Field(..., ge=0)
    code_quality_feedback: str = Field(default="")
    code_to_text_ratio: float = Field(default=0.0, ge=0.0, le=1.0)


# ==================== ANALYZER ====================
class TopicBreakdown(BaseModel):
    """Topic-level performance breakdown."""

    topic: str
    avg_score: float
    count: int


class FormatBreakdown(BaseModel):
    """Format-level performance breakdown."""

    format: str
    avg_score: float
    count: int


class AudienceBreakdown(BaseModel):
    """Audience segment performance breakdown."""

    segment: str
    avg_score: float
    count: int


class PeriodTrend(BaseModel):
    """Period-based trend analysis."""

    period: str
    avg_views: float
    avg_engagement: float


class LengthAnalysis(BaseModel):
    """Analysis by content length bucket."""

    bucket: str
    avg_score: float
    count: int


class AnalyzerOutput(BaseModel):
    """Output from content analyzer."""

    insights: list[str]
    top_topics: list[TopicBreakdown]
    top_formats: list[FormatBreakdown]
    audience_analysis: list[AudienceBreakdown]
    period_trends: list[PeriodTrend]
    length_analysis: list[LengthAnalysis]
    devrel_metrics: dict = Field(default_factory=dict)


# ==================== STRATEGIST ====================
class StrategistOutput(BaseModel):
    """Output from strategist agent."""

    gaps: list[str]
    reasons: list[str]

    @model_validator(mode="after")
    def validate_gaps_reasons_length(self) -> "StrategistOutput":
        """Ensure gaps and reasons have matching lengths."""
        if len(self.gaps) != len(self.reasons):
            raise ValueError("gaps and reasons must have equal length")
        return self


# ==================== REPORT ====================
class ContinueItem(BaseModel):
    """Content to continue producing."""

    topic: str
    format: str
    reason: str


class StopItem(BaseModel):
    """Content to stop producing."""

    topic: str
    format: str
    reason: str


class CreateNextItem(BaseModel):
    """New content to create."""

    topic: str
    format: str
    target_audience: str
    reasoning: str
    suggested_format: str = Field(default="tutorial")


class ReportOutput(BaseModel):
    """Final strategic report output."""

    report_date: date
    period: str
    summary: str
    continue_items: list[ContinueItem]
    stop_items: list[StopItem]
    create_next: list[CreateNextItem]


# ==================== TRACING ====================
class TraceEntry(BaseModel):
    """Execution trace entry for an agent."""

    agent: str
    input_summary: str
    output_summary: str
    duration_seconds: float
    status: str  # "success", "error", "fallback"


__all__ = [
    "RawContentRow",
    "CleanedContentRow",
    "PredictorInput",
    "PredictorOutput",
    "TopicBreakdown",
    "FormatBreakdown",
    "AudienceBreakdown",
    "PeriodTrend",
    "LengthAnalysis",
    "AnalyzerOutput",
    "StrategistOutput",
    "ContinueItem",
    "StopItem",
    "CreateNextItem",
    "ReportOutput",
    "TraceEntry",
]
