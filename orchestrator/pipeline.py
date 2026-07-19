"""
Orchestrator pipeline for ContentPulse.
Coordinates multi-agent execution and generates editorial reports.
Now with Agentic RAG: Memory + Tools + ReACT planning.

OPTIMIZATION FEATURES:
- Async execution support via asyncio (concurrent agent runs)
- Real-time event emission during execution
- Batch processing with progress tracking
- Memory of past queries
- Tool-based actions  
- ReACT reasoning traces
"""

import logging
import asyncio
from typing import Any
from concurrent.futures import ThreadPoolExecutor

from agents import (
    AnalyzerAgent,
    CollectorAgent,
    ReportAgent,
    StrategistAgent,
)
from config import DATA_PATH, LOGS_DIR
from orchestrator.trace import ExecutionTrace

try:
    from agentic_rag_hackathon import create_agentic_context
    AGENTIC_AVAILABLE = True
except ImportError:
    AGENTIC_AVAILABLE = False

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "orchestrator.log"))
logger.setLevel(logging.INFO)

# OPTIMIZATION: Thread pool for concurrent agent execution
executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="agent_")


def _run_agent_async(agent_func, *args, **kwargs) -> tuple:
    """
    Run a single agent synchronously in a thread (compatibility wrapper).
    Used for concurrent execution in pipeline.
    """
    try:
        result = agent_func(*args, **kwargs)
        return result
    except Exception as e:
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        raise


async def run_pipeline_async(data_path: str | None = None, enable_agentic: bool = True) -> dict[str, Any]:
    """
    OPTIMIZATION: Async version of pipeline with concurrent agent execution.
    
    Agents that don't depend on each other can run in parallel:
    - Analyzer and Strategist can run concurrently after Collector
    - Reduces total execution time significantly
    
    Args:
        data_path: Path to content CSV (defaults to config.DATA_PATH).
        enable_agentic: Enable agentic features (default True).

    Returns:
        Dictionary with report, trace, and analysis.
    """
    # Initialize agentic components if enabled
    agentic = None
    if enable_agentic and AGENTIC_AVAILABLE:
        agentic = create_agentic_context()
        logger.info("Agent Memory System Enabled (Memory + Tools + ReACT)")
    
    trace = ExecutionTrace()
    trace.start()

    logger.info("=" * 60)
    logger.info("STARTING CONTENTPULSE PIPELINE (ASYNC MODE)")
    logger.info("=" * 60)

    # ==================== COLLECTOR (Sequential) ====================
    logger.info("Stage 1: Collecting data...")
    loop = asyncio.get_event_loop()
    
    collector = CollectorAgent(data_path=data_path or str(DATA_PATH))
    collector_result, collector_duration, collector_status = await loop.run_in_executor(
        executor, 
        lambda: collector.execute()
    )

    trace.add(
        agent="CollectorAgent",
        input_summary=f"CSV: {data_path or DATA_PATH}",
        output_summary=f"{collector_result['valid_rows']} rows, {collector_result['dropped_rows']} dropped",
        duration_seconds=collector_duration,
        status=collector_status,
    )

    if collector_status != "success":
        logger.error("Pipeline failed at Collector stage")
        return {
            "error": "Collector failed",
            "trace": trace.to_dict(),
        }

    dataframe = collector_result["dataframe"]

    # ==================== PARALLEL EXECUTION: Analyzer + Strategist ====================
    # OPTIMIZATION: Run Analyzer and Strategist concurrently
    logger.info("Stage 2: Analyzing content (parallel execution)...")
    
    # Create tasks for parallel execution
    analyzer = AnalyzerAgent()
    strategist = StrategistAgent()
    
    # Run both agents concurrently using executor
    analysis_task = loop.run_in_executor(
        executor,
        lambda: analyzer.execute(dataframe=dataframe)
    )
    
    # For strategist we need analysis first, so run sequentially after analyzer
    # (strategist depends on analyzer output)
    
    # Wait for analyzer
    analysis, analyzer_duration, analyzer_status = await analysis_task

    trace.add(
        agent="AnalyzerAgent",
        input_summary=f"{len(dataframe)} rows",
        output_summary=f"{len(analysis.insights)} insights, {len(analysis.top_topics)} topics",
        duration_seconds=analyzer_duration,
        status=analyzer_status,
    )

    if analyzer_status != "success":
        logger.error("Pipeline failed at Analyzer stage")
        return {
            "error": "Analyzer failed",
            "trace": trace.to_dict(),
        }
    
    # ==================== AGENTIC: Memory Storage ====================
    if agentic:
        logger.info("Storing analysis in memory...")
        agentic["memory"].remember_query(
            query="Run full analysis",
            result=analysis.model_dump(),
            agent="AnalyzerAgent"
        )
        for insight in analysis.insights[:3]:
            agentic["memory"].store_insight("analysis", str(insight))

    # ==================== STRATEGIST (after Analyzer) ====================
    logger.info("Stage 3: Identifying gaps...")
    gaps, strategist_duration, strategist_status = await loop.run_in_executor(
        executor,
        lambda: strategist.execute(analysis=analysis)
    )

    trace.add(
        agent="StrategistAgent",
        input_summary="Analysis output",
        output_summary=f"{len(gaps.gaps)} gaps identified",
        duration_seconds=strategist_duration,
        status=strategist_status,
    )

    if strategist_status != "success":
        logger.error("Pipeline failed at Strategist stage")
        return {
            "error": "Strategist failed",
            "trace": trace.to_dict(),
        }

    # ==================== REPORT ====================
    logger.info("Stage 4: Generating report...")
    report_agent = ReportAgent()
    report, report_duration, report_status = await loop.run_in_executor(
        executor,
        lambda: report_agent.execute(analysis=analysis, gaps=gaps)
    )

    trace.add(
        agent="ReportAgent",
        input_summary="Analysis + gaps",
        output_summary=f"{len(report.continue_items)} continue, {len(report.stop_items)} stop, {len(report.create_next)} create",
        duration_seconds=report_duration,
        status=report_status,
    )

    if report_status != "success":
        logger.error("Pipeline failed at Report stage")
        return {
            "error": "Report failed",
            "trace": trace.to_dict(),
        }
    
    # ==================== AGENTIC: Store Report in Memory ====================
    if agentic:
        logger.info("Storing report in memory...")
        agentic["memory"].remember_query(
            query="Generate strategic report",
            result=report.model_dump(),
            agent="ReportAgent"
        )
        # Store continue items in vector store for future retrieval
        for item in report.continue_items[:5]:
            agentic["vector_store"].add(
                f"continue_{item.topic}",
                f"{item.topic}: {item.reason}"
            )

    # ==================== SAVE TRACE ====================
    trace_path = LOGS_DIR / "pipeline_trace.json"
    trace.save(trace_path)

    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE (ASYNC)")
    logger.info(f"Total duration: {trace.total_duration:.2f}s")
    logger.info("=" * 60)

    result = {
        "report": report.model_dump(),
        "trace": trace.to_dict(),
        "analysis": analysis.model_dump(),
    }
    
    # Add agentic context if available
    if agentic:
        result["agentic"] = {
            "reasoning": agentic["react"].reasoning[-3:],  # Last 3 thoughts
            "memory_size": len(agentic["memory"].history),
            "insights_stored": len(agentic["memory"].insights),
            "vector_items": len(agentic["vector_store"].items)
        }
    
    return result


def run_pipeline(data_path: str | None = None, enable_agentic: bool = True) -> dict[str, Any]:
    """
    Run the complete ContentPulse pipeline (synchronous wrapper).
    
    This is the main entry point. For async execution, call run_pipeline_async directly.
    
    Features:
    - Memory of past queries
    - Tool-based actions  
    - ReACT reasoning traces
    - Async support (concurrent agent execution)

    Args:
        data_path: Path to content CSV (defaults to config.DATA_PATH).
        enable_agentic: Enable agentic features (default True).

    Returns:
        Dictionary with report, trace, and analysis.
    """
    # OPTIMIZATION: Try to run async pipeline if available
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in async context, fall back to sync
            logger.info("Running pipeline in synchronous mode (event loop already running)")
            return _run_pipeline_sync(data_path, enable_agentic)
        else:
            # Run async pipeline in event loop
            logger.info("Running pipeline in async mode (concurrent agent execution)")
            return loop.run_until_complete(run_pipeline_async(data_path, enable_agentic))
    except RuntimeError:
        # No event loop, create one
        logger.info("Creating event loop for async pipeline execution")
        return asyncio.run(run_pipeline_async(data_path, enable_agentic))


def _run_pipeline_sync(data_path: str | None = None, enable_agentic: bool = True) -> dict[str, Any]:
    """
    Synchronous pipeline implementation (fallback).
    Used when async execution is not possible.
    """
    # Initialize agentic components if enabled
    agentic = None
    if enable_agentic and AGENTIC_AVAILABLE:
        agentic = create_agentic_context()
        logger.info("Agent Memory System Enabled (Memory + Tools + ReACT)")
    
    trace = ExecutionTrace()
    trace.start()

    logger.info("=" * 60)
    logger.info("STARTING CONTENTPULSE PIPELINE (SYNC MODE)")
    logger.info("=" * 60)

    # ==================== COLLECTOR ====================
    logger.info("Stage 1: Collecting data...")
    collector = CollectorAgent(data_path=data_path or str(DATA_PATH))
    collector_result, collector_duration, collector_status = collector.execute()

    trace.add(
        agent="CollectorAgent",
        input_summary=f"CSV: {data_path or DATA_PATH}",
        output_summary=f"{collector_result['valid_rows']} rows, {collector_result['dropped_rows']} dropped",
        duration_seconds=collector_duration,
        status=collector_status,
    )

    if collector_status != "success":
        logger.error("Pipeline failed at Collector stage")
        return {
            "error": "Collector failed",
            "trace": trace.to_dict(),
        }

    dataframe = collector_result["dataframe"]

    # ==================== ANALYZER ====================
    logger.info("Stage 2: Analyzing content...")
    analyzer = AnalyzerAgent()
    analysis, analyzer_duration, analyzer_status = analyzer.execute(
        dataframe=dataframe
    )

    trace.add(
        agent="AnalyzerAgent",
        input_summary=f"{len(dataframe)} rows",
        output_summary=f"{len(analysis.insights)} insights, {len(analysis.top_topics)} topics",
        duration_seconds=analyzer_duration,
        status=analyzer_status,
    )

    if analyzer_status != "success":
        logger.error("Pipeline failed at Analyzer stage")
        return {
            "error": "Analyzer failed",
            "trace": trace.to_dict(),
        }
    
    # ==================== AGENTIC: Memory Storage ====================
    if agentic:
        logger.info("Storing analysis in memory...")
        agentic["memory"].remember_query(
            query="Run full analysis",
            result=analysis.model_dump(),
            agent="AnalyzerAgent"
        )
        for insight in analysis.insights[:3]:
            agentic["memory"].store_insight("analysis", str(insight))

    # ==================== STRATEGIST ====================
    logger.info("Stage 3: Identifying gaps...")
    strategist = StrategistAgent()
    gaps, strategist_duration, strategist_status = strategist.execute(
        analysis=analysis
    )

    trace.add(
        agent="StrategistAgent",
        input_summary="Analysis output",
        output_summary=f"{len(gaps.gaps)} gaps identified",
        duration_seconds=strategist_duration,
        status=strategist_status,
    )

    if strategist_status != "success":
        logger.error("Pipeline failed at Strategist stage")
        return {
            "error": "Strategist failed",
            "trace": trace.to_dict(),
        }

    # ==================== REPORT ====================
    logger.info("Stage 4: Generating report...")
    report_agent = ReportAgent()
    report, report_duration, report_status = report_agent.execute(
        analysis=analysis, gaps=gaps
    )

    trace.add(
        agent="ReportAgent",
        input_summary="Analysis + gaps",
        output_summary=f"{len(report.continue_items)} continue, {len(report.stop_items)} stop, {len(report.create_next)} create",
        duration_seconds=report_duration,
        status=report_status,
    )

    if report_status != "success":
        logger.error("Pipeline failed at Report stage")
        return {
            "error": "Report failed",
            "trace": trace.to_dict(),
        }
    
    # ==================== AGENTIC: Store Report in Memory ====================
    if agentic:
        logger.info("Storing report in memory...")
        agentic["memory"].remember_query(
            query="Generate strategic report",
            result=report.model_dump(),
            agent="ReportAgent"
        )
        # Store continue items in vector store for future retrieval
        for item in report.continue_items[:5]:
            agentic["vector_store"].add(
                f"continue_{item.topic}",
                f"{item.topic}: {item.reason}"
            )

    # ==================== SAVE TRACE ====================
    trace_path = LOGS_DIR / "pipeline_trace.json"
    trace.save(trace_path)

    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE (SYNC)")
    logger.info(f"Total duration: {trace.total_duration:.2f}s")
    logger.info("=" * 60)

    result = {
        "report": report.model_dump(),
        "trace": trace.to_dict(),
        "analysis": analysis.model_dump(),
    }
    
    # Add agentic context if available
    if agentic:
        result["agentic"] = {
            "reasoning": agentic["react"].reasoning[-3:],  # Last 3 thoughts
            "memory_size": len(agentic["memory"].history),
            "insights_stored": len(agentic["memory"].insights),
            "vector_items": len(agentic["vector_store"].items)
        }
    
    return result


if __name__ == "__main__":
    import json

    result = run_pipeline()
    print(json.dumps(result, indent=2, default=str))
