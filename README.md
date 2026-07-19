# ContentPulse — Editorial AI Strategy Platform

## 🚀 Overview

**ContentPulse** is a multi-agent AI system that translates content performance data into actionable editorial decisions. It analyzes historical content metrics, identifies performance patterns, predicts new content performance, and generates strategic recommendations for content teams.

### Key Features
- 📊 **Real-time Analytics**: Aggregates content performance across topics, formats, and audiences
- 🎯 **Performance Prediction**: Predicts scores for draft content using comparable historical data
- 🔍 **Gap Analysis**: Identifies content opportunities (trending topics, underperforming areas)
- 📋 **Strategic Reports**: Generates editorial recommendations (Continue, Stop, Create)
- 🧠 **Multi-Agent Architecture**: Specialized agents for data collection, analysis, prediction, and strategy
- 🎨 **Interactive Dashboard**: Dark-themed single-page app with real-time insights
- 📈 **Execution Tracing**: Full visibility into pipeline performance and decisions

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    ContentPulse Platform                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────── Data Layer ──────────────────────┐   │
│  │  Hacker News API → CSV → Pydantic Validation         │   │
│  │  200 articles across 10 tech topics                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                  │
│  ┌──────────────────── Agent Pipeline ──────────────────┐   │
│  │  1. CollectorAgent    → Load & enrich data           │   │
│  │  2. AnalyzerAgent     → Compute insights             │   │
│  │  3. PredictorAgent    → Score draft content          │   │
│  │  4. StrategistAgent   → Identify gaps               │   │
│  │  5. ReportAgent       → Generate recommendations     │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                  │
│  ┌──────────────────── Flask API ──────────────────────┐    │
│  │  /api/report  →  Full pipeline execution            │    │
│  │  /api/score   →  Single content prediction          │    │
│  │  /api/topics  →  Config endpoints                   │    │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                  │
│  ┌──────────────────── Dashboard UI ──────────────────┐     │
│  │  📊 Dashboard    (Metrics, Charts, Insights)        │     │
│  │  ✍️  Draft Scorer  (Form, Prediction, Ring)         │     │
│  │  🎯 Strategy      (Continue, Stop, Create Cards)   │     │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Module Structure

```
contentpulse/
├── config.py                    # Central configuration (topics, formats, weights)
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
│
├── data/
│   ├── schema.py               # Pydantic v2 models (15+)
│   ├── integrate_data.py       # HN API fetcher & transformer
│   └── sample_content_data.csv # 200 articles dataset
│
├── agents/
│   ├── base_agent.py           # ABC with execute() wrapper
│   ├── collector.py            # Load, validate, enrich data
│   ├── analyzer.py             # Vectorized aggregations
│   ├── predictor.py            # Fuzzy matching, scoring
│   ├── strategist.py           # Gap identification
│   └── report.py               # Strategic recommendations
│
├── llm/
│   ├── client.py               # Google Generative AI wrapper
│   └── __init__.py             # Exports
│
├── orchestrator/
│   ├── pipeline.py             # Run full 4-agent pipeline
│   ├── scorer.py               # Single content prediction
│   ├── trace.py                # Execution tracing
│   └── __init__.py             # Exports
│
├── ui/
│   ├── api_server.py           # Flask API (POST /report, /score)
│   ├── index.html              # Dashboard SPA
│   ├── index.css               # Glassmorphic dark theme
│   └── app.js                  # State + tab management
│
├── tests/
│   ├── test_schema.py          # 17 schema validation tests
│   ├── test_agents.py          # 13 agent integration tests
│   └── __init__.py             # Test module marker
│
├── logs/                        # Runtime logs
├── assets/                      # Screenshots, videos, exports
└── .git/                        # Version control
```

---

## 🔄 Data Flow

### Stage 1: Data Collection
**CollectorAgent** loads content from CSV and enriches with derived fields.

```
CSV (200 rows)
    ↓
Validate against RawContentRow schema
    ↓
Vectorized transformations:
    • length_bucket       (short/medium/long/evergreen)
    • publish_month       (YYYY-MM)
    • publish_quarter     (YYYY-Qn)
    • days_since_publish  (clipped ≥1)
    • views_per_day       (views / days)
    ↓
Performance Score (0-100):
    • Normalize: views, engagement_rate, conversions, search_rank
    • Weight: 0.4*views + 0.3*engagement + 0.2*conversions + 0.1*rank
    • Multiply by 100, round 1 decimal
    ↓
CleanedContentRow DataFrame (200 rows, 18 columns)
```

### Stage 2: Analysis
**AnalyzerAgent** aggregates performance across 5 dimensions.

```
DataFrame (200 rows)
    ↓
Vectorized groupby aggregations:
    • top_topics[10]        → avg_score, count per topic
    • top_formats[5]        → avg_score, count per format
    • audience_analysis[4]  → avg_score, count per segment
    • period_trends[N]      → avg_views, avg_engagement per quarter
    • length_analysis[4]    → avg_score per bucket (ordered)
    ↓
Build compact summary (no raw rows, only aggregates)
    ↓
LLM call:
    system: "You are a content analytics expert. Return JSON: {\"insights\": [...]}"
    user:   "Aggregated data:\n{summary}\nReturn 4-6 insights."
    ↓
Parse JSON → 6 insights OR fallback to 6 deterministic insights
    ↓
AnalyzerOutput:
    • insights[6]           ← LLM or fallback
    • top_topics[10]
    • top_formats[5]
    • audience_analysis[4]
    • period_trends[N]
    • length_analysis[4]
```

### Stage 3: Prediction
**PredictorAgent** predicts performance of draft content.

```
Draft content:
    {title, topic, format, audience_segment, word_count}
    ↓
Find comparable historical rows (fuzzy matching):
    Level 1: topic + format + audience    (try to get ≥3)
    Level 2: topic + format                (if <3, relax)
    Level 3: topic                         (if still <3, relax)
    Fallback: return score=50, conf=low    (if <3 total)
    ↓
Build summary from matches:
    • count, mean/std/min/max/median score
    • avg views, avg engagement, avg word_count
    • best format
    ↓
LLM call (max_tokens=400):
    system: "You are a content predictor. Return JSON: {...}"
    user:   "Proposed content: {...}\nComparable data: {...}"
    ↓
Parse JSON → predicted_score, reasoning, suggestions[3], confidence
    OR statistical fallback: median score, confidence by N
    ↓
PredictorOutput:
    • predicted_score       (0-100)
    • reasoning             (1 sentence)
    • suggestions[3]        (exactly 3 items)
    • confidence            (high/medium/low)
    • comparable_count      (N)
```

### Stage 4: Strategy
**StrategistAgent** identifies content gaps and opportunities.

```
AnalyzerOutput (top_topics, insights)
    ↓
Build context:
    • covered_topics = set(all topics in analysis)
    • topic_scores = dict(topic → avg_score)
    ↓
Gap Detection:
    For each trending topic NOT covered:
        gap = "{topic}"
        reason = "Zero coverage, first-mover opportunity"
    
    For each covered topic with score < 40:
        gap = "{topic}"
        reason = "Low score {X:.1f}, consider refreshing"
    ↓
Fallback (if no gaps):
    gaps = ["No critical gaps detected"]
    reasons = ["Current portfolio covers key topics"]
    ↓
StrategistOutput:
    • gaps[N]               (gap descriptions)
    • reasons[N]            (1:1 parity with gaps)
```

### Stage 5: Report
**ReportAgent** generates strategic editorial recommendations.

```
AnalyzerOutput + StrategistOutput
    ↓
Build decisions:
    Continue (score ≥ 60):
        ContinueItem(topic, format, "score {X:.1f} above threshold")
    
    Stop (score < 35):
        StopItem(topic, format, "score {X:.1f} below threshold")
    
    Create (for each gap):
        CreateNextItem(gap, format, audience, reason)
    ↓
Generate summary:
    "Recommend continuing {top_continue}. Pause {stop_count} streams.
     Launch {create_count} new topics."
    ↓
ReportOutput:
    • report_date           (today)
    • period                ("Last 12 months")
    • summary               (executive summary)
    • continue_items[N]     (green: invest more)
    • stop_items[N]         (red: pause)
    • create_next[N]        (amber: new opportunities)
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- macOS/Linux (tested on macOS)
- Git

### 1. Clone & Setup

```bash
git clone <repo-url>
cd contentpulse
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env:
#   GOOGLE_API_KEY=your-key-here (optional, use mock mode if empty)
#   MOCK_LLM=true                 (default, no real API calls)
```

### 3. Load Data

```bash
PYTHONPATH=. python3 data/integrate_data.py
# Output: 200 rows in data/sample_content_data.csv + assets/data/hackernews_export.csv
```

### 4. Run Tests

```bash
PYTHONPATH=. python3 -m pytest tests/ -v
# Expected: 30 passed
```

---

## 🚀 Usage

### Option 1: Interactive Dashboard (Recommended)

```bash
source venv/bin/activate
PYTHONPATH=. python3 -m ui.api_server
# Visit http://localhost:5050
```

Then in browser:
1. **Dashboard Tab**: Click "Run Analysis" → See metrics, charts, insights, trace
2. **Draft Scorer Tab**: Fill form → Click "Score This Draft" → See prediction + suggestions
3. **Strategy Tab**: Click "Generate Report" → See Continue/Stop/Create cards

### Option 2: Command-Line API

```bash
source venv/bin/activate
PYTHONPATH=. python3 << 'EOF'
from orchestrator import run_pipeline, score_draft

# Full analysis
result = run_pipeline()
print(f"Report: {result['report']['summary']}")
print(f"Trace: {result['trace']['total_duration_seconds']:.2f}s")

# Single prediction
pred = score_draft(
    title="AI Agents Guide",
    topic="AI/ML",
    fmt="blog",
    audience_segment="developers",
    word_count=2000
)
print(f"Score: {pred['prediction']['predicted_score']}")
EOF
```

### Option 3: Programmatic Access

```python
from agents import CollectorAgent, AnalyzerAgent, StrategistAgent, ReportAgent
from config import DATA_PATH

# Collect data
c = CollectorAgent(str(DATA_PATH))
result, dur, status = c.execute()
df = result['dataframe']

# Analyze
a = AnalyzerAgent()
analysis, _, _ = a.execute(dataframe=df)
print(f"Insights: {analysis.insights}")

# Strategy
s = StrategistAgent()
gaps, _, _ = s.execute(analysis=analysis)
print(f"Gaps: {gaps.gaps}")

# Report
r = ReportAgent()
report, _, _ = r.execute(analysis=analysis, gaps=gaps)
print(f"Continue: {len(report.continue_items)}")
```

---

## 📊 Configuration

### `config.py` Constants

```python
TOPICS                    # 10 tech topics
FORMATS                   # 7 content types (blog, video, etc.)
AUDIENCE_SEGMENTS         # 4 segments (developers, managers, executives, general_tech)
PERFORMANCE_WEIGHTS       # {views: 0.4, engagement_rate: 0.3, conversions: 0.2, search_rank: 0.1}
LLM_PROVIDER             # "gemini"
LLM_MODEL                # "gemini-2.0-flash"
MOCK_LLM                 # true/false (default: true)
DATA_PATH                # Path to CSV
LOGS_DIR                 # Path to logs/
ASSETS_DIR               # Path to assets/
```

### Environment Variables (`.env`)

```bash
GOOGLE_API_KEY=your-gemini-api-key
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash
MOCK_LLM=true
DATA_PATH=data/sample_content_data.csv
```

---

## 📈 Data Schema

### Input: RawContentRow (CSV)

| Field | Type | Validation |
|-------|------|-----------|
| title | str | 1-200 chars |
| url | str | Regex: ^https?:// |
| topic | str | Must be in TOPICS |
| format | str | Must be in FORMATS |
| audience_segment | str | Must be in AUDIENCE_SEGMENTS |
| word_count | int | 100-20000 |
| publish_date | date | No future dates |
| views | int | ≥0 |
| engagement_rate | float | 0.0-1.0 |
| avg_time_on_page | float | ≥0 |
| conversions | int | ≥0 |
| search_rank | int? | 1-100 (optional) |

### Output: CleanedContentRow (Derived)

Adds 6 computed fields:
- **length_bucket** → "short" / "medium" / "long" / "evergreen"
- **publish_month** → "YYYY-MM"
- **publish_quarter** → "YYYY-Qn"
- **days_since_publish** → int (≥1)
- **views_per_day** → float (views / days)
- **performance_score** → float (0-100, weighted metric)

---

## 🧠 Agents Explained

### 1. CollectorAgent
**Responsibility**: Load, validate, and enrich raw content data.

```python
execute() → {
    "dataframe": DataFrame (200 rows, 18 cols),
    "total_rows": 200,
    "valid_rows": 200,
    "dropped_rows": 0
}
```

**Key operations**:
- Vectorized whitespace stripping
- Schema validation (Pydantic)
- Derived field computation (no loops)
- Min-max normalization → performance_score

**Performance**: <0.05s for 200 rows

---

### 2. AnalyzerAgent
**Responsibility**: Compute insights from historical data.

```python
execute(dataframe=df) → AnalyzerOutput {
    "insights": [...],           # 6 LLM insights or fallback
    "top_topics": [...],         # 10 topics with scores
    "top_formats": [...],        # 5 formats with scores
    "audience_analysis": [...],  # 4 segments with scores
    "period_trends": [...],      # Quarterly trends
    "length_analysis": [...]     # Length bucket analysis
}
```

**Key operations**:
- Pandas groupby aggregations (no loops)
- LLM call for insights (with JSON parsing fallback)
- 6 deterministic fallback insights if LLM fails

**Performance**: <0.01s for 200 rows

---

### 3. PredictorAgent
**Responsibility**: Predict performance of draft content.

```python
execute(
    dataframe=df,
    title="...", topic="AI/ML", format="blog",
    audience_segment="developers", word_count=1500
) → PredictorOutput {
    "predicted_score": 78,
    "reasoning": "Similar content averaged 78/100...",
    "suggestions": ["Add code...", "Include benchmarks...", "Optimize..."],
    "confidence": "high",
    "comparable_count": 12
}
```

**Key operations**:
- Fuzzy matching (3 relaxation levels)
- LLM prediction with max_tokens=400
- Statistical fallback (median score + best practices)
- Confidence: high (N≥20), medium (N≥10), low (N<10)

**Performance**: <0.01s

---

### 4. StrategistAgent
**Responsibility**: Identify content gaps and opportunities.

```python
execute(analysis=analysis) → StrategistOutput {
    "gaps": ["FinOps", "AI Agents", "Platform Engineering", ...],
    "reasons": [
        "Zero coverage of trending topic 'FinOps'...",
        "Zero coverage of trending topic 'AI Agents'...",
        ...
    ]
}
```

**Key operations**:
- Gap detection: 6 trending topics not in coverage
- Gap detection: topics with score < 40 (refresh candidates)
- Ensures gaps.length == reasons.length (validated by schema)

**Trending topics**: FinOps, AI Agents, Platform Engineering, WebAssembly, Edge Computing, Green Software

---

### 5. ReportAgent
**Responsibility**: Generate editorial recommendations.

```python
execute(analysis=analysis, gaps=gaps) → ReportOutput {
    "report_date": "2026-07-19",
    "period": "Last 12 months",
    "summary": "Recommend continuing Mobile. Pause 1 stream. Launch 12 new topics.",
    "continue_items": [
        {topic: "Mobile", format: "blog", reason: "Score 44.5 above..."},
        ...
    ],
    "stop_items": [
        {topic: "Platform", format: "blog", reason: "Score 32.8 below..."},
        ...
    ],
    "create_next": [
        {topic: "FinOps", format: "blog", target_audience: "developers", reasoning: "..."},
        ...
    ]
}
```

**Thresholds**:
- **Continue**: score ≥ 60
- **Stop**: score < 35
- **Create**: For each gap (1:1 mapping)

---

## 🎨 Dashboard UI

### Theme

```css
Background:        #0b0d12 (near-black)
Surface:           rgba(22, 26, 36, 0.72) (glassmorphic)
Primary (Green):   #48c482
Text:              #e2e8f0 (light slate)
Text Dim:          #94a3b8 (muted)
Red (Stop):        #ef5350
Amber (Create):    #fbbf24
```

### 3 Tabs

#### 📊 Dashboard
- **4 Metric Cards**: Articles, Topics, Key Insights, Content Gaps
- **2 Charts**: Topic Performance (bar), Format Performance (bar)
- **Insights List**: 6 LLM-generated insights
- **Execution Trace**: Agent execution times and status

#### ✍️ Draft Scorer
- **Form**: Title, Topic (select), Format (select), Audience (select), Word Count
- **Result Card** (hidden until scored):
  - SVG Score Ring (0-100, animated stroke)
  - Confidence Badge (high=green, medium=amber, low=red)
  - 3 Recommendations
  - Comparable Count

#### 🎯 Strategy Report
- **Report Header**: Summary, period, date
- **3 Color-Coded Cards**:
  - 🟢 **Continue** (green border): Topics to keep investing
  - 🔴 **Stop** (red border): Topics to pause
  - 🟡 **Create** (amber border): New opportunities
- **Execution Trace**: Full pipeline timing

### Responsive Design
- **Desktop** (>768px): Multi-column grid, smooth animations
- **Tablet** (481-768px): 2-column metrics, single-column charts
- **Mobile** (<480px): All single-column, optimized touch targets

---

## 🔐 Error Handling & Fallbacks

### LLM Layer
```
Real API call (if MOCK_LLM=false)
    ↓ (on error)
    Fallback: return hardcoded JSON
    ↓ (with logging)
    Continue pipeline
```

### Data Validation
```
Pydantic schema validation
    ↓ (invalid row)
    Log debug message
    ↓ (skip row)
    Continue with valid rows
```

### Agent Execution
```
try: run()
except Exception:
    status = "error"
    result = {"error": str(e)}
    log full traceback
    return (result, duration, status)
```

### Prediction Fallback
```
LLM call succeeds
    ↓ (fails)
    JSON parse error
    ↓ (use statistical fallback)
    median score, best-practice suggestions
```

---

## 🧪 Testing

### Test Suite: 30 Tests

**tests/test_schema.py** (17 tests)
- RawContentRow: URL, topic, format, date, views validation
- CleanedContentRow: Derived fields, length buckets
- PredictorInput/Output: Structure, suggestion count
- StrategistOutput: Gap/reason parity
- ReportOutput, AnalyzerOutput: Structure

**tests/test_agents.py** (13 tests)
- CollectorAgent: Data loading, columns, score range, no nulls
- AnalyzerAgent: Aggregations, fallback insights, LLM chain
- PredictorAgent: Existing topic, unknown combo
- StrategistAgent: Gap identification
- ReportAgent: Report generation
- Orchestrator: Full pipeline, scorer CLI

### Running Tests

```bash
# All tests
PYTHONPATH=. python3 -m pytest tests/ -v

# Specific file
PYTHONPATH=. python3 -m pytest tests/test_schema.py -v

# With coverage
PYTHONPATH=. python3 -m pytest tests/ --cov=agents --cov=data
```

### Expected Output
```
============================= 30 passed in 2.14s ==============================
```

---

## 📝 API Reference

### REST Endpoints

#### `GET /api/topics`
Returns list of available topics.

```bash
curl http://localhost:5050/api/topics
# ["AI/ML", "DevOps", "Cloud", ...]
```

#### `GET /api/formats`
Returns list of available formats.

```bash
curl http://localhost:5050/api/formats
# ["blog", "video", "infographic", ...]
```

#### `GET /api/audiences`
Returns list of audience segments.

```bash
curl http://localhost:5050/api/audiences
# ["developers", "managers", "executives", "general_tech"]
```

#### `POST /api/report`
Runs full pipeline: collect → analyze → strategize → report.

```bash
curl -X POST http://localhost:5050/api/report \
  -H 'Content-Type: application/json' \
  -d '{}'

# Response:
{
  "report": { report_date, period, summary, continue_items, stop_items, create_next },
  "analysis": { insights, top_topics, top_formats, ... },
  "trace": { entries, total_duration_seconds, entry_count, timestamp }
}
```

#### `POST /api/score`
Predicts performance of draft content.

```bash
curl -X POST http://localhost:5050/api/score \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Building AI Agents",
    "topic": "AI/ML",
    "format": "blog",
    "audience_segment": "developers",
    "word_count": 1500
  }'

# Response:
{
  "prediction": {
    "predicted_score": 78,
    "reasoning": "Similar AI/ML blog posts...",
    "suggestions": ["Add code...", "Include benchmarks...", "Optimize..."],
    "confidence": "high",
    "comparable_count": 12
  },
  "trace": { ... }
}
```

### Error Responses

**400 Bad Request** (missing fields)
```json
{
  "error": "Missing required fields: title, topic"
}
```

**500 Internal Server Error**
```json
{
  "error": "Server error"
}
```

---

## 📚 Key Concepts

### Performance Score (0-100)

Multi-metric scoring formula:
```
views_norm = MinMax(views) ∈ [0,1]
engagement_norm = MinMax(engagement_rate) ∈ [0,1]
conversions_norm = MinMax(conversions) ∈ [0,1]
rank_norm = 1 - MinMax(search_rank) ∈ [0,1]  # Inverted (lower rank is better)

score = (0.4 × views_norm + 0.3 × engagement_norm + 0.2 × conversions_norm + 0.1 × rank_norm) × 100
```

### Fuzzy Matching (Prediction)

Progressive relaxation to find comparable content:
```
Ideal:       topic + format + audience_segment  (try this first)
            ↓ if <3 rows
Relax:       topic + format                      (try this)
            ↓ if <3 rows
Ultra-relax: topic                               (try this)
            ↓ if <3 rows
Fallback:    score=50, confidence=low
```

### Confidence Levels

Based on comparable content count:
- **high**: N ≥ 20 (strong historical data)
- **medium**: N ≥ 10 (moderate data)
- **low**: N < 10 (scarce data)

### Trending Topics

Topics not yet covered but gaining industry momentum:
- FinOps
- AI Agents
- Platform Engineering
- WebAssembly
- Edge Computing
- Green Software

---

## 🚨 Troubleshooting

### "MOCK_LLM not set, but GOOGLE_API_KEY missing"
**Fix**: Set `MOCK_LLM=true` in `.env` or provide a valid API key.

### "Connection refused" to Flask server
**Fix**: Ensure the server is running:
```bash
PYTHONPATH=. python3 -m ui.api_server
```

### "Only N < 3 rows found" warning in predictor
**Expected**: Happens with niche topic/format/audience combos. Uses fallback.

### CSV validation errors
**Check**: Ensure CSV has all 12 required columns and valid data types.

### LLM timeout
**Expected** (mock mode): Returns hardcoded response instantly.
**Real mode**: May take 2-5 seconds per call.

---

## 🎯 Production Deployment

### Recommended Setup

```bash
# 1. Use real Google Generative AI key
export MOCK_LLM=false
export GOOGLE_API_KEY=sk-xxx

# 2. Use production-grade WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5050 ui.api_server:app

# 3. Set up logging & monitoring
export LOG_LEVEL=INFO
tail -f logs/orchestrator.log

# 4. Cache results for repeated reports
# (Not yet implemented, add Redis)
```

---

## 📖 Example Workflows

### Workflow 1: Editorial Team Review

1. **Morning Standup**: Run dashboard analysis
   - Check top performers (Continue items)
   - Identify underperformers (Stop items)
   - Review new opportunities (Create items)

2. **Content Planning**: Score drafts before publication
   - Writer submits draft
   - Score it with Draft Scorer
   - Get actionable suggestions before publish

3. **Strategy Meeting**: Use Strategy Report
   - Quarterly review of coverage
   - Identify gaps vs. competitors
   - Plan new content series

### Workflow 2: Data-Driven Publishing

```
Content Calendar  →  Draft Scorer  →  Score ≥ 75?  →  Publish
                                              ↓
                                           Adjust & Re-score
```

### Workflow 3: Continuous Optimization

```
Week 1: Publish content using scorer predictions
Week 2: Collect performance data
Week 3: Run full analysis pipeline
Week 4: Update strategy based on gaps
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Write tests for new functionality
4. Ensure `pytest` passes
5. Submit a PR

---

## 📄 License

MIT License — See LICENSE file for details.

---

## 📞 Support

For issues or questions:
1. Check **Troubleshooting** section above
2. Review **Data Flow** to understand pipeline
3. Run tests: `PYTHONPATH=. python3 -m pytest tests/ -v`
4. Check logs in `logs/` directory

---

## 🗺️ Roadmap

- [ ] Redis caching for repeated reports
- [ ] Multi-user workspace support
- [ ] Custom topic/format/audience definitions
- [ ] A/B testing analytics
- [ ] Content calendar export
- [ ] Slack integration for alerts
- [ ] Real-time content performance dashboard
- [ ] Automated report scheduling

---

**Happy analyzing! 🚀**
