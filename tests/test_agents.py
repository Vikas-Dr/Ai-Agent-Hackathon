"""
Tests for agents.
"""

import pytest

from agents import (
    AnalyzerAgent,
    CollectorAgent,
    PredictorAgent,
    ReportAgent,
    StrategistAgent,
)
from config import DATA_PATH


@pytest.fixture
def dataframe():
    """Load and prepare test dataframe."""
    collector = CollectorAgent(data_path=str(DATA_PATH))
    result, _, _ = collector.execute()
    return result["dataframe"]


@pytest.fixture
def analysis(dataframe):
    """Generate analysis for tests."""
    analyzer = AnalyzerAgent()
    result, _, _ = analyzer.execute(dataframe=dataframe)
    return result


@pytest.fixture
def gaps(analysis):
    """Generate gaps for tests."""
    strategist = StrategistAgent()
    result, _, _ = strategist.execute(analysis=analysis)
    return result


class TestCollectorAgent:
    """Test CollectorAgent."""

    def test_loads_data(self):
        """Test that collector loads data."""
        collector = CollectorAgent(data_path=str(DATA_PATH))
        result, _, status = collector.execute()
        assert status == "success"
        assert result["valid_rows"] > 0
        assert "dataframe" in result

    def test_derived_columns(self, dataframe):
        """Test that derived columns are present."""
        required_cols = [
            "length_bucket",
            "publish_month",
            "publish_quarter",
            "days_since_publish",
            "views_per_day",
            "performance_score",
        ]
        for col in required_cols:
            assert col in dataframe.columns

    def test_score_range(self, dataframe):
        """Test performance score is in valid range."""
        assert (dataframe["performance_score"] >= 0).all()
        assert (dataframe["performance_score"] <= 100).all()

    def test_no_null_scores(self, dataframe):
        """Test no null performance scores."""
        assert dataframe["performance_score"].isna().sum() == 0


class TestAnalyzerAgent:
    """Test AnalyzerAgent."""

    def test_aggregations(self, analysis):
        """Test that analyzer computes aggregations."""
        assert len(analysis.insights) > 0
        assert len(analysis.top_topics) > 0
        assert len(analysis.top_formats) > 0
        assert len(analysis.audience_analysis) > 0

    def test_fallback_insights(self, dataframe):
        """Test fallback insight generation."""
        analyzer = AnalyzerAgent()
        insights = analyzer._generate_fallback_insights(dataframe)
        assert len(insights) == 6

    def test_llm_fallback_chain(self, analysis):
        """Test that insights are generated (either LLM or fallback)."""
        assert isinstance(analysis.insights, list)
        assert len(analysis.insights) >= 4


class TestPredictorAgent:
    """Test PredictorAgent."""

    def test_predict_existing_topic(self, dataframe):
        """Test prediction for existing topic."""
        predictor = PredictorAgent()
        result, _, status = predictor.execute(
            dataframe=dataframe,
            title="AI/ML Article",
            topic="API Design",
            format="technical_blog",
            audience_segment="backend",
            word_count=1500,
        )
        assert status == "success"
        assert 0 <= result.predicted_score <= 100
        assert len(result.suggestions) == 3

    def test_predict_unknown_topic_default(self, dataframe):
        """Test prediction with unknown combination."""
        predictor = PredictorAgent()
        result, _, status = predictor.execute(
            dataframe=dataframe,
            title="Unknown",
            topic="API Design",
            format="podcast",
            audience_segment="architects",
            word_count=10000,
        )
        assert status == "success"
        assert 0 <= result.predicted_score <= 100


class TestStrategistAgent:
    """Test StrategistAgent."""

    def test_identifies_gaps(self, analysis):
        """Test that strategist identifies gaps."""
        strategist = StrategistAgent()
        result, _, status = strategist.execute(analysis=analysis)
        assert status == "success"
        assert len(result.gaps) > 0
        assert len(result.gaps) == len(result.reasons)


class TestReportAgent:
    """Test ReportAgent."""

    def test_generates_report(self, analysis, gaps):
        """Test that report agent generates valid report."""
        report_agent = ReportAgent()
        result, _, status = report_agent.execute(analysis=analysis, gaps=gaps)
        assert status == "success"
        assert len(result.continue_items) >= 0
        assert len(result.stop_items) >= 0
        assert len(result.create_next) >= 0
        assert result.report_date is not None


class TestOrchestrator:
    """Test orchestrator pipeline."""

    def test_pipeline_end_to_end(self):
        """Test full pipeline execution."""
        from orchestrator import run_pipeline

        result = run_pipeline(data_path=str(DATA_PATH))
        assert "report" in result
        assert "trace" in result
        assert "analysis" in result
        assert len(result["trace"]["entries"]) == 4  # 4 agents

    def test_scorer(self):
        """Test content scorer."""
        from orchestrator import score_draft

        result = score_draft(
            title="Test Article",
            topic="API Design",
            fmt="blog",
            audience_segment="backend",
            word_count=1500,
            data_path=str(DATA_PATH),
        )
        assert "prediction" in result
        assert "trace" in result
        assert result["prediction"]["predicted_score"] >= 0
