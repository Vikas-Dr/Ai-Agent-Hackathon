DEVPULSE - Developer Relations Content Intelligence

Overview

DevPulse is a multi-agent AI system for developer relations (DevRel) teams. It translates developer content performance data into actionable editorial decisions, focusing on API adoption, SDK/framework coverage, developer experience metrics, and GitHub engagement.

Core Capabilities

- Memory System: Agent remembers past queries and insights
- Semantic Search: Find similar content without exact matching
- ReACT Reasoning: Shows thinking through THOUGHT > ACTION > OBSERVATION
- Tool Registry: Extensible, pluggable tools
- Multi-Turn Conversations: Context-aware follow-ups

Architecture

System Design

The platform consists of:

Data Layer
- Hacker News API integration
- CSV data (200 articles)
- DevRel metrics collection
- Pydantic validation

Intelligence Layer
- Memory System for context retention
- ReACT Planner for multi-step reasoning
- Vector Search for semantic matching
- Tool Registry for extensibility

Agent Pipeline
1. CollectorAgent - Load and enrich data
2. AnalyzerAgent - DevRel metrics and insights
3. PredictorAgent - Code analysis and scoring
4. StrategistAgent - SDK/framework gap identification
5. ReportAgent - DevRel recommendations

Interfaces
- Flask API with REST endpoints
- Interactive dashboard UI
- Command-line tools

Module Structure

devpulse/
- config.py: Central configuration
- requirements.txt: Python dependencies
- .env.example: Environment template

data/
- schema.py: Pydantic models
- integrate_data.py: HN API fetcher
- sample_content_data.csv: 200 articles dataset

agents/
- base_agent.py: Base agent class
- collector.py: Data loading
- analyzer.py: Metrics and aggregations
- predictor.py: Code analysis and scoring
- strategist.py: Gap identification
- report.py: Strategy recommendations

llm/
- client.py: Google Gemini and HuggingFace
- __init__.py: Exports

orchestrator/
- pipeline.py: Full pipeline execution
- scorer.py: Single content prediction
- trace.py: Execution tracing
- __init__.py: Exports

agentic_rag_hackathon.py: Core agentic system (450 LOC)

ui/
- api_server.py: Flask API
- index.html: Dashboard SPA
- index.css: Styling
- app.js: Frontend logic

utils/
- code_parser.py: Markdown code analysis

tests/
- test_schema.py: Schema validation
- test_agents.py: Agent integration

logs/: Runtime logs
assets/: Screenshots, exports

Installation and Setup

Prerequisites

- Python 3.11+
- macOS/Linux or Windows with WSL
- 4GB RAM minimum
- Git

Quick Start (5 minutes)

1. Clone and enter directory
git clone <repo-url>
cd devpulse

2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Configure environment
cp .env.example .env

5. Load data
PYTHONPATH=. python3 data/integrate_data.py

6. See it work
python run_hackathon.py --demo

Usage

Option 1: Interactive Dashboard

Start the server:
PYTHONPATH=. python3 -m ui.api_server

Then visit: http://localhost:5050

Tabs available:
- Dashboard: DevRel Metrics, Insights
- Draft Scorer: Code Analysis, Prediction
- Strategy: Continue/Stop/Create Cards
- Chat: Multi-turn conversation with memory

Option 2: Quick Demo

python run_hackathon.py --demo

Shows all features working in 2 minutes.

Option 3: Full Pipeline

python run_hackathon.py --pipeline

Runs complete analysis with agentic features.

Option 4: Command-Line API

from orchestrator import run_pipeline

result = run_pipeline(enable_agentic=True)
print(f"Report: {result['report']['summary']}")
print(f"Memory size: {result['agentic']['memory_size']}")

Option 5: Programmatic Access

from agents import CollectorAgent, AnalyzerAgent

c = CollectorAgent(str(DATA_PATH))
result, dur, status = c.execute()
df = result['dataframe']

a = AnalyzerAgent()
analysis, _, _ = a.execute(dataframe=df)
print(f"Insights: {analysis.insights}")

Features

Memory System

Agent remembers past queries and insights.

Usage:
from agentic_rag_hackathon import QuickMemory

memory = QuickMemory()

memory.remember_query(
    query="What topics are trending?",
    result={"insights": ["API Design +20%"]},
    agent="AnalyzerAgent"
)

memory.store_insight("trends", "API Design growing")

print(memory.get_context())

Semantic Search

Find similar content without exact matching.

Usage:
from agentic_rag_hackathon import QuickVectorStore

store = QuickVectorStore()

store.add("api_design", "Building RESTful APIs")
store.add("web_apis", "Creating web service APIs")

results = store.search("API development", k=2)

ReACT Reasoning

Agent shows its thinking process.

Usage:
from agentic_rag_hackathon import create_agentic_context

agentic = create_agentic_context()
thoughts = agentic["react"].think_and_act("What's missing?", "AnalyzerAgent")

for thought in thoughts["thoughts"]:
    print(thought)

Tool Registry

Extensible, pluggable tools.

Usage:
from agentic_rag_hackathon import ToolKit

tools = ToolKit()
tools.add_tool("search", lambda q: find_similar(q))
tools.add_tool("summarize", lambda t: summarize(t))

result = tools.call("search", q="API design")

Configuration

config.py Constants

TOPICS: 10 DevRel topics (API Design, Authentication, Cloud Infrastructure, etc.)

FORMATS: 7 content types (technical_blog, tutorial, code_example, etc.)

AUDIENCE_SEGMENTS: 4 developer roles (frontend, backend, devops, architects)

PERFORMANCE_WEIGHTS: {views: 0.30, engagement: 0.25, conversions: 0.25, rank: 0.10}

TRENDING_TOPICS: FinOps, AI Agents, Platform Engineering, WebAssembly, etc.

Environment Variables (.env)

MOCK_LLM=true (use mock, no API calls)
GOOGLE_API_KEY=your-key (for real LLM)
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
DATA_PATH=data/sample_content_data.csv

Agents

1. Collector Agent

Loads and cleans the content dataset.

Input: CSV file with 200 articles
Output: Validated DataFrame with 18 columns
Performance: Less than 0.05s for 200 rows

Adds derived fields: length_bucket, publish_month, performance_score

2. Analyzer Agent

Computes insights from historical data.

Input: DataFrame from Collector
Output: AnalyzerOutput with insights, top_topics, top_formats
Performance: Less than 0.01s for 200 rows

Uses LLM for insight generation with fallback

3. Predictor Agent

Predicts performance of draft content.

Input: Draft {title, topic, format, audience, word_count}
Output: PredictorOutput with score, reasoning, suggestions
Performance: Less than 0.01s

Uses fuzzy matching and vector search for similar content

4. Strategist Agent

Identifies content gaps and opportunities.

Input: AnalyzerOutput
Output: StrategistOutput with gaps and reasons
Performance: Less than 0.01s

Compares covered vs trending topics

5. Report Agent

Generates strategic recommendations.

Input: AnalyzerOutput and StrategistOutput
Output: ReportOutput with continue/stop/create items
Performance: Less than 0.01s

No redundant LLM calls, just assembles results

Dashboard UI

Theme

Background: Dark (#0b0d12)
Surface: Glassmorphic overlay
Primary: Green (#48c482)
Text: Light slate (#e2e8f0)
Accents: Red for stop, Amber for create

Tabs

Dashboard: Metrics, charts, insights, execution trace
Draft Scorer: Form input, prediction score, recommendations
Strategy Report: Continue/Stop/Create cards
Chat: Multi-turn conversation with memory

Responsive Design

Desktop (>768px): Multi-column grid
Tablet (481-768px): 2-column metrics
Mobile (<480px): Single-column, touch-optimized

Testing

Test Suite

30+ tests covering:
- Schema validation (17 tests)
- Agent functionality (13 tests)

Running Tests

PYTHONPATH=. python3 -m pytest tests/ -v

Expected: 30 passed

API Reference

Endpoints

GET /api/topics
Returns available topics list

GET /api/formats
Returns available formats list

GET /api/audiences
Returns audience segments

POST /api/report
Runs full pipeline with optional agentic features
Parameters: enable_agentic (boolean)

POST /api/score
Predicts performance of draft content
Parameters: title, topic, format, audience_segment, word_count, draft_markdown (optional)

Troubleshooting

Issue: "Module not found"
Solution: export PYTHONPATH=.

Issue: "No API key"
Solution: Set MOCK_LLM=true in .env

Issue: "Port in use"
Solution: Kill process or use different port

Issue: "Data missing"
Solution: Run python3 data/integrate_data.py

Issue: "Tests failing"
Solution: Check requirements.txt versions match

Support

1. Check README.md Troubleshooting section
2. Review Data Flow to understand pipeline
3. Run tests: PYTHONPATH=. pytest tests/ -v
4. Check logs in logs/ directory
5. Read INSTALL.md for detailed setup

Roadmap

- Memory system with SQLite (in progress)
- Redis caching for repeated reports
- Multi-user workspace support
- Custom topic/format/audience definitions
- A/B testing analytics
- Content calendar export
- Slack integration for alerts
- Real-time content performance dashboard
- Automated report scheduling

License

MIT License - See LICENSE file

Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests
4. Ensure pytest passes
5. Submit pull request

Summary

DevPulse is a complete multi-agent AI system for developer relations with integrated memory, semantic search, reasoning capabilities, and extensible tools.

Ready for production deployment.

Status: Complete and tested
Setup time: 5 minutes
Demo time: 2 minutes
Production ready: Yes
