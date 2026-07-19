"""
Tests for data schemas.
"""

from datetime import date, timedelta

import pytest

from data.schema import (
    AnalyzerOutput,
    AudienceBreakdown,
    CleanedContentRow,
    FormatBreakdown,
    LengthAnalysis,
    PeriodTrend,
    PredictorInput,
    PredictorOutput,
    RawContentRow,
    ReportOutput,
    StrategistOutput,
    TopicBreakdown,
    ContinueItem,
)


class TestRawContentRow:
    """Test RawContentRow validation."""

    def test_valid_row(self):
        """Test valid raw content row."""
        d = date.today() - timedelta(days=30)
        row = RawContentRow(
            title="Test Article",
            url="https://example.com/test",
            topic="AI/ML",
            format="blog",
            audience_segment="developers",
            word_count=1000,
            publish_date=d,
            views=100,
            engagement_rate=0.1,
            avg_time_on_page=60,
            conversions=5,
            search_rank=10,
        )
        assert row.title == "Test Article"
        assert row.views == 100

    def test_invalid_url(self):
        """Test invalid URL validation."""
        d = date.today() - timedelta(days=30)
        with pytest.raises(ValueError):
            RawContentRow(
                title="Test",
                url="not-a-url",  # No http/https
                topic="AI/ML",
                format="blog",
                audience_segment="developers",
                word_count=1000,
                publish_date=d,
                views=100,
                engagement_rate=0.1,
                avg_time_on_page=60,
                conversions=5,
            )

    def test_invalid_topic(self):
        """Test invalid topic validation."""
        d = date.today() - timedelta(days=30)
        with pytest.raises(ValueError):
            RawContentRow(
                title="Test",
                url="https://example.com",
                topic="InvalidTopic",
                format="blog",
                audience_segment="developers",
                word_count=1000,
                publish_date=d,
                views=100,
                engagement_rate=0.1,
                avg_time_on_page=60,
                conversions=5,
            )

    def test_invalid_format(self):
        """Test invalid format validation."""
        d = date.today() - timedelta(days=30)
        with pytest.raises(ValueError):
            RawContentRow(
                title="Test",
                url="https://example.com",
                topic="AI/ML",
                format="invalid",
                audience_segment="developers",
                word_count=1000,
                publish_date=d,
                views=100,
                engagement_rate=0.1,
                avg_time_on_page=60,
                conversions=5,
            )

    def test_future_date(self):
        """Test future date validation."""
        d = date.today() + timedelta(days=5)
        with pytest.raises(ValueError):
            RawContentRow(
                title="Test",
                url="https://example.com",
                topic="AI/ML",
                format="blog",
                audience_segment="developers",
                word_count=1000,
                publish_date=d,
                views=100,
                engagement_rate=0.1,
                avg_time_on_page=60,
                conversions=5,
            )

    def test_negative_views(self):
        """Test negative views validation."""
        d = date.today() - timedelta(days=30)
        with pytest.raises(ValueError):
            RawContentRow(
                title="Test",
                url="https://example.com",
                topic="AI/ML",
                format="blog",
                audience_segment="developers",
                word_count=1000,
                publish_date=d,
                views=-100,
                engagement_rate=0.1,
                avg_time_on_page=60,
                conversions=5,
            )

    def test_optional_search_rank(self):
        """Test optional search_rank field."""
        d = date.today() - timedelta(days=30)
        row = RawContentRow(
            title="Test",
            url="https://example.com",
            topic="AI/ML",
            format="blog",
            audience_segment="developers",
            word_count=1000,
            publish_date=d,
            views=100,
            engagement_rate=0.1,
            avg_time_on_page=60,
            conversions=5,
            search_rank=None,
        )
        assert row.search_rank is None


class TestCleanedContentRow:
    """Test CleanedContentRow derivation."""

    def test_derived_fields(self):
        """Test that derived fields are computed."""
        d = date.today() - timedelta(days=30)
        row = CleanedContentRow(
            title="Test",
            url="https://example.com",
            topic="AI/ML",
            format="blog",
            audience_segment="developers",
            word_count=1500,
            publish_date=d,
            views=1000,
            engagement_rate=0.15,
            avg_time_on_page=120,
            conversions=50,
        )
        assert row.length_bucket == "long"
        assert row.publish_month is not None
        assert row.publish_quarter is not None
        assert row.days_since_publish == 30
        assert row.views_per_day > 0
        assert row.performance_score == 0.0  # Placeholder

    def test_length_buckets(self):
        """Test length bucket categorization."""
        d = date.today()
        short = CleanedContentRow(
            title="Short", url="https://x.com", topic="AI/ML", format="blog",
            audience_segment="developers", word_count=300, publish_date=d,
            views=100, engagement_rate=0.1, avg_time_on_page=60, conversions=5
        )
        medium = CleanedContentRow(
            title="Medium", url="https://x.com", topic="AI/ML", format="blog",
            audience_segment="developers", word_count=1000, publish_date=d,
            views=100, engagement_rate=0.1, avg_time_on_page=60, conversions=5
        )
        long = CleanedContentRow(
            title="Long", url="https://x.com", topic="AI/ML", format="blog",
            audience_segment="developers", word_count=2500, publish_date=d,
            views=100, engagement_rate=0.1, avg_time_on_page=60, conversions=5
        )
        evergreen = CleanedContentRow(
            title="Evergreen", url="https://x.com", topic="AI/ML", format="blog",
            audience_segment="developers", word_count=5000, publish_date=d,
            views=100, engagement_rate=0.1, avg_time_on_page=60, conversions=5
        )
        assert short.length_bucket == "short"
        assert medium.length_bucket == "medium"
        assert long.length_bucket == "long"
        assert evergreen.length_bucket == "evergreen"


class TestPredictorSchema:
    """Test Predictor schemas."""

    def test_valid_input(self):
        """Test valid predictor input."""
        inp = PredictorInput(
            title="Test",
            topic="AI/ML",
            format="blog",
            audience_segment="developers",
            word_count=1500,
        )
        assert inp.topic == "AI/ML"

    def test_invalid_topic(self):
        """Test invalid predictor topic."""
        with pytest.raises(ValueError):
            PredictorInput(
                title="Test",
                topic="Invalid",
                format="blog",
                audience_segment="developers",
                word_count=1500,
            )

    def test_valid_output(self):
        """Test valid predictor output."""
        out = PredictorOutput(
            predicted_score=75,
            reasoning="Good match",
            suggestions=["s1", "s2", "s3"],
            confidence="high",
            comparable_count=10,
        )
        assert out.predicted_score == 75
        assert len(out.suggestions) == 3

    def test_output_wrong_suggestions_count(self):
        """Test predictor output with wrong suggestion count."""
        with pytest.raises(ValueError):
            PredictorOutput(
                predicted_score=75,
                reasoning="Test",
                suggestions=["s1", "s2"],  # Only 2, needs 3
                confidence="high",
                comparable_count=10,
            )


class TestStrategistOutput:
    """Test StrategistOutput validation."""

    def test_matching_lengths(self):
        """Test matching gaps and reasons."""
        output = StrategistOutput(
            gaps=["gap1", "gap2"],
            reasons=["reason1", "reason2"],
        )
        assert len(output.gaps) == 2
        assert len(output.reasons) == 2

    def test_mismatched_lengths(self):
        """Test mismatched gaps and reasons."""
        with pytest.raises(ValueError):
            StrategistOutput(
                gaps=["gap1", "gap2"],
                reasons=["reason1"],  # Mismatch
            )


class TestReportOutput:
    """Test ReportOutput."""

    def test_valid_report(self):
        """Test valid report output."""
        report = ReportOutput(
            report_date=date.today(),
            period="Q1",
            summary="Test summary",
            continue_items=[
                ContinueItem(topic="AI/ML", format="blog", reason="Test")
            ],
            stop_items=[],
            create_next=[],
        )
        assert len(report.continue_items) == 1
        assert report.report_date == date.today()


class TestAnalyzerOutput:
    """Test AnalyzerOutput."""

    def test_valid(self):
        """Test valid analyzer output."""
        output = AnalyzerOutput(
            insights=["insight1"],
            top_topics=[TopicBreakdown(topic="AI/ML", avg_score=50.0, count=10)],
            top_formats=[FormatBreakdown(format="blog", avg_score=50.0, count=10)],
            audience_analysis=[
                AudienceBreakdown(segment="developers", avg_score=50.0, count=10)
            ],
            period_trends=[
                PeriodTrend(period="2026-Q1", avg_views=100.0, avg_engagement=0.1)
            ],
            length_analysis=[
                LengthAnalysis(bucket="short", avg_score=50.0, count=5)
            ],
        )
        assert len(output.insights) == 1
        assert len(output.top_topics) == 1
