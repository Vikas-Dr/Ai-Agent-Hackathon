# DevPulse Architecture

## System Overview

DevPulse is a multi-agent AI system that analyzes developer relations content and provides actionable editorial strategies. It combines semantic search, multi-agent reasoning, and business logic to deliver content intelligence.

```
┌─────────────────────────────────────────────────────────┐
│              DevPulse System Architecture               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Data Layer  │  │ Intelligence │  │  Interfaces  │  │
│  │              │  │    Layer     │  │              │  │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤  │
│  │ • CSV Data   │  │ • Memory     │  │ • REST API   │  │
│  │ • Hacker News│  │ • ReACT      │  │ • Dashboard  │  │
│  │ • Metrics    │  │ • Vector DB  │  │ • CLI Tools  │  │
│  │ • Pydantic   │  │ • Tools      │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         ↓                  ↓                  ↓         │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Agent Pipeline                          │   │
│  │  Collector → Analyzer → Predictor → Strategist →   │
│  │  ├─ Enriches Data        ├─ Metrics      │      │   │
│  │  └─ Validates            └─ Insights     └─ Report  │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Data Layer (`/data`)
- **CSV Integration**: 200+ articles with DevRel metrics
- **Hacker News API**: Real-time content trends
- **Validation**: Pydantic models for data quality
- **Files**: 
  - `sample_content_data.csv` - Article performance data
  - `integrate_data.py` - Data processing pipeline

### 2. Intelligence Layer
- **Memory System** (`/memory`): Persistent agent context
- **Retrieval** (`/retrieval`): Semantic search & vector matching
- **Orchestration** (`/orchestrator`): Multi-agent coordination
- **Planning** (`/planning`): ReACT reasoning engine

### 3. Agent Pipeline (`/agents`)
1. **CollectorAgent**: Load, validate, and enrich raw data
2. **AnalyzerAgent**: Extract DevRel metrics and generate insights
3. **PredictorAgent**: Analyze code patterns and predict engagement
4. **StrategistAgent**: Identify content gaps and SDK coverage
5. **ReportAgent**: Generate strategic recommendations

### 4. API & UI
- **REST API** (`/ui/api_server.py`): Flask backend with endpoints
- **Dashboard** (`/ui`): Interactive React-based interface
- **Configuration** (`config.py`): Centralized settings

## File Structure

```
devpulse/
├── README.md                 # Main project documentation
├── INSTALL.md               # Installation & setup guide
├── ARCHITECTURE.md          # This file - System design
├── requirements.txt         # Python dependencies
├── config.py               # Configuration center
│
├── agents/                 # Multi-agent system
│   ├── report.py          # Report generation
│   └── ...                # Other agent implementations
│
├── data/                   # Data processing
│   ├── sample_content_data.csv
│   └── integrate_data.py
│
├── llm/                    # LLM integrations
│   └── client.py          # OpenAI, Claude, Gemini
│
├── retrieval/              # Vector search & semantic matching
│   ├── chroma_client.py
│   └── vector_utils.py
│
├── memory/                 # Agent memory system
│   └── agent_memory.py
│
├── orchestrator/           # Agent coordination
│   └── agent_orchestrator.py
│
├── planning/               # ReACT reasoning
│   └── react_planner.py
│
├── tools/                  # Tool registry & implementations
│   ├── calculator.py
│   ├── search.py
│   └── ...
│
├── ui/                     # Web interface
│   ├── index.html         # Dashboard UI
│   ├── app.js             # Frontend logic
│   ├── index.css          # Styling
│   └── api_server.py      # Flask backend
│
├── utils/                  # Utilities
│   └── ...
│
└── logs/                   # Application logs
    └── api_server.log
```

## Key Features

### 1. Content Analysis
- Topic performance ranking
- Format effectiveness comparison
- Audience segment analysis
- Quarterly trend tracking

### 2. Strategic Recommendations
- Content gap identification
- SDK/framework coverage analysis
- Editorial priority ranking (Continue/Stop/Create)
- Engagement predictions

### 3. Interactive Dashboard
- Real-time metrics visualization
- 2x2 Content Strategy Matrix
- KPI trend indicators (↑/↓/→)
- A/B testing interface
- Custom dataset analysis

### 4. Developer-Friendly Tools
- Draft scoring with code analysis
- Comparable content suggestions
- GitHub issue export
- CSV data import

## Configuration

All settings are centralized in `config.py`:
- API credentials (OpenAI, Gemini, etc.)
- Data paths and sources
- LLM model selection
- Vector database settings
- Flask server configuration

Use `.env` for sensitive values:
```bash
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
DATABASE_URL=postgresql://...
```

## Quick Start

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Configure credentials**: Copy `.env.example` to `.env` and fill in API keys
3. **Run API server**: `python ui/api_server.py`
4. **Access dashboard**: Open `http://localhost:5000`
5. **Run analysis**: Click "Run Analysis" button

## Development Workflow

### Adding a New Agent
1. Create agent file in `/agents`
2. Inherit from base agent class
3. Implement required methods (init, execute, observe)
4. Register in orchestrator

### Adding a New Tool
1. Create tool file in `/tools`
2. Implement tool interface
3. Add to tool registry
4. Update agent access list

### Testing
- Use demo scripts: `python simple_demo.py`
- Check API endpoints: `curl http://localhost:5000/api/health`
- View logs: `tail -f logs/api_server.log`

## Environment

- **Python**: 3.9+
- **Framework**: Flask (API), vanilla JS (Frontend)
- **LLM**: Multi-provider (OpenAI, Gemini, Claude)
- **Vector DB**: Chroma
- **Task Queue**: Optional Celery for background jobs

## Support

- For bugs: Check `logs/` directory
- For API help: See INSTALL.md
- For architecture questions: Review this document
