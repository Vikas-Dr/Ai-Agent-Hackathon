# 📊 DevPulse — Developer Relations Content Intelligence

**A production-ready dashboard for analyzing, scoring, and optimizing developer content strategy using AI-powered insights.**

![DevPulse](https://img.shields.io/badge/DevPulse-v1.0-48c482?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-2.0+-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

---

## 🎯 What is DevPulse?

DevPulse is a comprehensive platform for developer relations teams to:

- **📊 Analyze Content Performance** — Understand topic, format, and audience trends across your content library
- **⭐ Score Draft Content** — Get AI-powered predictions on how well a piece of content will perform before publishing
- **🔀 Run A/B Tests** — Compare headlines and code hooks to find what resonates with developers
- **📤 Upload Custom Data** — Analyze your company's own content metrics with DevPulse
- **🎯 Generate Strategy Reports** — Get actionable editorial recommendations based on data

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **pip** (Python package manager)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

### Installation & Setup

#### 1. Clone or Download the Repository

```bash
cd DevPulse
```

#### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Start the API Server

```bash
python ui/api_server.py
```

You'll see output like:

```
 * Running on http://0.0.0.0:5050
 * Press CTRL+C to quit
```

#### 5. Open the Dashboard

Open your browser and navigate to:

```
http://localhost:5050
```

You should see the DevPulse dashboard with the following tabs:
- 📊 **Dashboard** — View analytics and metrics
- ✍️ **Draft Scorer** — Score your content
- 🔀 **A/B Tester** — Test headlines and code
- 📤 **Custom Data** — Upload your own CSV data
- 🎯 **Strategy Report** — Generate recommendations
- 📋 **Data Table** — Browse full dataset

---

## 📋 Features Overview

### 1. Dashboard (📊)

Real-time analytics dashboard showing:

- **Metric Cards** with trend indicators
  - Articles Analyzed
  - Topics Covered
  - Key Insights
  - Content Gaps
- **Charts & Visualizations**
  - Topic Performance (bar chart)
  - Format Distribution (doughnut chart)
  - Quarterly Trends (line chart)
  - Audience Reach analysis
- **Content Strategy Matrix** — Visualize content by engagement vs. relevance
- **Key Insights** — AI-generated strategic recommendations
- **Execution Trace** — See step-by-step analysis pipeline

**How to Use:**

1. Click the **"🔄 Run Analysis"** button to analyze the default HackerNews dataset
2. View real-time metrics and charts as they populate
3. Explore insights and strategy recommendations
4. Export analysis as JSON

### 2. Draft Scorer (✍️)

Score your content idea before publishing:

- **Form Fields:**
  - Article Title
  - Topic (dropdown)
  - Format (dropdown)
  - Audience Segment (dropdown)
  - Word Count (numeric)
  - Draft Markdown (optional)
  - Asset Upload (screenshot/video)

- **Score Output:**
  - Predicted performance score (0-100)
  - Code quality ratio (if markdown provided)
  - Confidence level
  - Comparable historical content
  - Recommendations

**How to Use:**

1. Fill in the form with your content details
2. Click **"📈 Score This Draft"**
3. View your predicted score and recommendations
4. Compare against historical content

### 3. A/B Tester (🔀)

Test multiple headline and code hook variants:

- **Test 3 headline variants** to find the best opening
- **Compare 2 code hooks** for developer engagement
- **Get recommendations** on which combination performs best

**How to Use:**

1. Enter your headline variants (or use defaults)
2. Enter code hook variants (or use defaults)
3. Click **"🔀 Run A/B Test"**
4. View winner recommendations and scoring breakdown

### 4. Custom Data Upload (📤)

Analyze your company's content with your own CSV data:

**Required CSV Columns:**

```
- title              (Article title)
- url                (Article URL)
- score              (Performance metric: views, HN score, etc.)
- engagement_rate    (Engagement percentage)
- conversions        (Conversion count)
- topic              (Content topic)
- format             (Content format)
- audience_segment   (Target audience)
```

**How to Use:**

1. Prepare a CSV file with your content data
2. Click the upload zone (or drag-drop)
3. Click **"🚀 Run Custom Analysis"**
4. View analysis results specific to your data

### 5. Strategy Report (🎯)

Generate comprehensive editorial strategy recommendations:

- Strategic priorities for topics and formats
- Content gaps and opportunities
- Audience segment recommendations
- Publication cadence analysis
- Actionable next steps

**Export Options:**

- 📥 **Export PDF** — Download full report as PDF
- 📋 **GitHub Issues** — Export recommendations as GitHub issues
- 📋 **Copy Summary** — Copy text to clipboard

**How to Use:**

1. Click **"📊 Generate Report"**
2. Review strategic recommendations
3. Export in your preferred format

### 6. Data Table (📋)

Browse and sort the full dataset:

- View all analyzed content
- Sort by any column (Title, Topic, Format, etc.)
- Search and filter capabilities
- Download dataset

---

## ⚙️ API Endpoints Reference

All endpoints are accessible at `http://localhost:5050/api/`

### Configuration Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/topics` | GET | Get available topics |
| `/api/formats` | GET | Get available content formats |
| `/api/audiences` | GET | Get audience segments |

### Analysis Endpoints

| Endpoint | Method | Description | Body |
|----------|--------|-------------|------|
| `/api/report` | POST | Run full analysis pipeline | `{}` |
| `/api/data` | GET | Get full dataset | — |
| `/api/score` | POST | Score a draft | See below |

### Score Endpoint Request Body

```json
{
  "title": "Building REST APIs with FastAPI",
  "topic": "Backend Development",
  "format": "Tutorial",
  "audience_segment": "Intermediate",
  "word_count": 1500,
  "draft_markdown": "# My Article\n\nContent here...",
  "asset_path": "/path/to/screenshot.png"
}
```

### Upload Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload-csv` | POST | Upload custom CSV dataset |
| `/api/upload-asset` | POST | Upload screenshot/video for scoring |

---

## 🎨 Dashboard UI Features

### Modern Design System

- **Dark Theme** with vibrant accent colors
- **Glassmorphism Cards** with backdrop blur effects
- **Smooth Animations** for all transitions
- **Responsive Layout** — works on desktop, tablet, and mobile
- **Real-time Updates** with visual indicators
- **Interactive Charts** powered by Chart.js

### Visual Elements

- **Metric Cards** with sparkline trends
- **Strategy Matrix** showing 2x2 content positioning
- **Trend Indicators** with up/down arrows
- **Toast Notifications** for success/error feedback
- **Loading Spinners** during analysis
- **Empty States** with helpful prompts

---

## 🏗️ Project Architecture

### Frontend

```
ui/
├── index.html      # Main dashboard HTML (6 tabs)
├── app.js          # JavaScript logic (1,886 lines)
└── index.css       # Styling & animations (1,982 lines)
```

### Backend

```
├── ui/api_server.py        # Flask API server (346 lines)
├── orchestrator/           # Pipeline orchestration
│   ├── pipeline.py         # Main analysis pipeline
│   ├── scorer.py           # Content scoring logic
│   └── trace.py            # Execution tracing
├── agents/                 # AI agents
│   ├── collector.py        # Data collection
│   ├── analyzer.py         # Content analysis
│   ├── predictor.py        # Score prediction
│   ├── strategist.py       # Strategy generation
│   └── ...
├── data/                   # Data processing
├── retrieval/              # Vector search
├── memory/                 # RAG memory system
└── llm/                    # LLM client
```

### Configuration

```
config.py              # Global configuration
requirements.txt       # Python dependencies
.env / .env.example    # Environment variables
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# API Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5050
FLASK_DEBUG=False

# Data Configuration
DATA_PATH=assets/data/

# Logging
LOG_LEVEL=INFO
```

Copy `.env.example` to `.env` if provided.

### Python Configuration

Edit `config.py` to customize:

```python
# Topics, formats, and audiences
TOPICS = ["Backend Development", "Frontend Development", ...]
FORMATS = ["Blog Post", "Tutorial", "Video", ...]
AUDIENCE_SEGMENTS = ["Beginner", "Intermediate", "Advanced"]

# Directories
ASSETS_DIR = Path(__file__).parent / "assets"
LOGS_DIR = Path(__file__).parent / "logs"
```

---

## 📊 Data Structure

### Analysis Result Format

The pipeline returns a structured result:

```python
{
    "report": {
        "summary": "...",
        "top_topics": [...],
        "top_formats": [...],
        "insights": [...],
        "create_next": [...]  # Content gap recommendations
    },
    "analysis": {
        "top_topics": [...],
        "top_formats": [...],
        "audiences": [...],
        "quarterly_data": {...},
        "length_distribution": {...},
        "period_trends": [...],
        "insights": [...]
    },
    "trace": {
        "steps": [...]  # Execution trace for debugging
    }
}
```

---

## 🚨 Troubleshooting

### Server Won't Start

**Error:** `Address already in use`

**Solution:**
```bash
# On macOS/Linux:
lsof -ti :5050 | xargs kill -9

# On Windows:
netstat -ano | findstr :5050
taskkill /PID <PID> /F
```

Then restart:

```bash
python ui/api_server.py
```

### Dashboard Shows "No Data Yet"

**Solution:** Click the **"🔄 Run Analysis"** button in the Dashboard tab to load the default dataset.

### Scoring Endpoint Returns Error

**Check:**
- All required fields are provided (title, topic, format, audience_segment, word_count)
- Topic, format, and audience_segment values match available options
- Word count is between 100-20,000

### Charts Not Displaying

**Solution:**
1. Check browser console for errors (F12 → Console)
2. Ensure Chart.js CDN is loaded (check Network tab)
3. Try refreshing the page (Ctrl+Shift+R)

### Custom CSV Upload Fails

**Check:**
- CSV file has required columns: `title`, `url`, `score`, `engagement_rate`, `conversions`, `topic`, `format`, `audience_segment`
- File size is under 50MB
- File is valid CSV format (no encoding issues)

---

## 📁 File Organization

```
DevPulse/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── config.py                      # Configuration
├── ui/
│   ├── api_server.py             # Flask server
│   ├── index.html                # Dashboard UI
│   ├── app.js                    # JavaScript logic
│   └── index.css                 # Styling
├── orchestrator/                 # Pipeline orchestration
├── agents/                       # AI agents
├── data/                         # Data processing
├── retrieval/                    # Vector search
├── memory/                       # RAG memory
├── llm/                          # LLM client
├── utils/                        # Utilities
├── tools/                        # Tool registry
├── assets/                       # Data & uploads
│   ├── data/                     # Sample datasets
│   └── user_uploads/             # Custom uploads
└── logs/                         # Application logs
```

---

## 🔗 Quick Links

- **Dashboard:** http://localhost:5050
- **API Base:** http://localhost:5050/api
- **Topics Endpoint:** http://localhost:5050/api/topics
- **Formats Endpoint:** http://localhost:5050/api/formats
- **Audiences Endpoint:** http://localhost:5050/api/audiences

---

## 📝 Example Workflows

### Workflow 1: Analyze Performance

1. Go to **Dashboard** tab
2. Click **"🔄 Run Analysis"**
3. Review metrics, charts, and insights
4. Click **"📥 Export JSON"** to save results

### Workflow 2: Score Your Idea

1. Go to **Draft Scorer** tab
2. Fill in your content details
3. Paste your draft markdown (optional)
4. Click **"📈 Score This Draft"**
5. View score and recommendations

### Workflow 3: Test Headlines

1. Go to **A/B Tester** tab
2. Enter 3 headline variants
3. Enter 2 code hook variants
4. Click **"🔀 Run A/B Test"**
5. View winner and scoring breakdown

### Workflow 4: Analyze Custom Data

1. Go to **Custom Data** tab
2. Upload your CSV file
3. Click **"🚀 Run Custom Analysis"**
4. Review analysis specific to your data

### Workflow 5: Generate Strategy

1. Go to **Strategy Report** tab
2. Click **"📊 Generate Report"**
3. Review recommendations
4. Export as PDF or GitHub Issues

---

## 🛠️ Development

### Adding New Topics/Formats/Audiences

Edit `config.py`:

```python
TOPICS = ["Topic 1", "Topic 2", ...]
FORMATS = ["Format 1", "Format 2", ...]
AUDIENCE_SEGMENTS = ["Segment 1", "Segment 2", ...]
```

Restart the server:

```bash
python ui/api_server.py
```

### Extending the Dashboard

1. **Add new charts:** Edit `ui/app.js` and add Chart.js rendering
2. **Modify styles:** Edit `ui/index.css`
3. **Update HTML:** Edit `ui/index.html` to add new elements
4. **Add new tabs:** Duplicate an existing section in HTML and add event listeners in JavaScript

### Adding Custom Agents

Create new agent files in `agents/` directory:

```python
# agents/my_agent.py
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def execute(self):
        # Your logic here
        return result, trace, metadata
```

Register in the pipeline (`orchestrator/pipeline.py`).

---

## 📦 Dependencies

Key dependencies (see `requirements.txt` for full list):

- **Flask** — Web framework for API server
- **Chart.js** — Frontend charting library (CDN)
- **pandas** — Data processing
- **scikit-learn** — Machine learning
- **numpy** — Numerical computing
- **python-dotenv** — Environment management

---

## 🤝 Support & Feedback

For issues, questions, or feature requests:

1. Check this README for troubleshooting
2. Review logs in `logs/` directory
3. Check browser console (F12) for frontend errors

---

## 📄 License

MIT License — See LICENSE file for details.

---

## 🎉 Get Started

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start server
python ui/api_server.py

# 3. Open browser
# http://localhost:5050

# 4. Click "Run Analysis" to begin!
```

**Happy analyzing!** 🚀

---

**DevPulse v1.0** — Built for data-driven developer relations teams.
