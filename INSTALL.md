# DevPulse Local Setup Guide

## Prerequisites

- **Python 3.10+** — [Download Python](https://www.python.org/downloads/)
- **Git** — [Download Git](https://git-scm.com/downloads)
- **Text Editor** — VS Code, PyCharm, or any IDE
- **API Keys** (optional, can use mock mode):
  - Google API: https://aistudio.google.com/app/apikey
  - HuggingFace Token: https://huggingface.co/settings/tokens

---

## Quick Setup (Automated)

### 1. Clone the Repository
```bash
git clone https://github.com/Vikas-Dr/Ai-Agent-Hackathon.git
cd Ai-Agent-Hackathon
```

### 2. Run Quick Start Script
```bash
python quickstart.py
```

This will:
- ✅ Verify Python 3.10+
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create .env configuration file
- ✅ Verify project structure

---

## Manual Setup (Step-by-Step)

### 1. Clone Repository
```bash
git clone https://github.com/Vikas-Dr/Ai-Agent-Hackathon.git
cd Ai-Agent-Hackathon
```

### 2. Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create .env File
Create a file named `.env` in the project root with:

```
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
GOOGLE_API_KEY=your_api_key_here
HF_TOKEN=your_hf_token_here
MOCK_LLM=true
DATA_PATH=data/sample_content_data.csv
```

**Note:** You can leave API keys blank and use `MOCK_LLM=true` to test locally.

### 5. Generate Sample Data
```bash
PYTHONPATH=. python data/integrate_data.py
```

This fetches real Hacker News stories and creates `data/sample_content_data.csv`

### 6. Start the Dashboard
```bash
PYTHONPATH=. python ui/api_server.py
```

Output should show:
```
 * Running on http://127.0.0.1:5050
 * Press CTRL+C to quit
```

### 7. Open in Browser
```
http://localhost:5050
```

---

## Directory Structure

```
Ai-Agent-Hackathon/
├── agents/                 # Content analysis agents
│   ├── analyzer.py        # DevRel metrics & insights
│   ├── predictor.py       # Content scoring with code analysis
│   ├── strategist.py      # Gap detection & strategy
│   ├── report.py          # Recommendations & GitHub export
│   └── sdk_detector.py    # SDK deprecation flagging
│
├── ui/                    # Web dashboard
│   ├── index.html         # Main interface (4 tabs)
│   ├── app.js             # Dashboard logic + A/B tester
│   ├── api_server.py      # FastAPI backend
│   └── index.css          # Styling
│
├── data/                  # Data layer
│   ├── schema.py          # Pydantic models (DevRel metrics)
│   ├── integrate_data.py  # HN data integration
│   └── collector.py       # Data collection
│
├── utils/                 # Helper modules
│   ├── code_parser.py     # Markdown code block analyzer
│   ├── ab_tester.py       # A/B testing simulator
│   ├── intent_extractor.py   # Developer intent classification
│   ├── sandbox_generator.py  # 10-line starter code templates
│   └── sdk_detector.py    # SDK deprecation detector
│
├── orchestrator/          # Pipeline orchestration
│   ├── __init__.py        # Main pipeline
│   └── scorer.py          # Draft scoring engine
│
├── llm/                   # LLM integration
│   ├── client.py          # Gemini + HuggingFace client
│   └── __init__.py
│
├── config.py              # DevRel configuration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md              # Project documentation
```

---

## Features Overview

### 📊 Dashboard Tab
- View content analytics
- Topic & format distribution
- Audience insights
- Performance metrics

### ✍️ Draft Scorer Tab
- Score article drafts
- Analyze code-to-text ratio
- Get AI recommendations
- Get code quality feedback

### 🔀 A/B Tester Tab
- Test 3 headline variants
- Test 2 code hooks
- Compare side-by-side
- Get winner + combined score

### 🎯 Strategy Report Tab
- Generate editorial recommendations
- See what to continue/stop/create
- Export as GitHub Issues
- Bi-weekly action plan

---

## Troubleshooting

### Import Errors
```bash
# Make sure PYTHONPATH is set
PYTHONPATH=. python ui/api_server.py
```

### Port 5050 Already in Use
Edit `ui/api_server.py`, find:
```python
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050)
```
Change port to 5051, 5052, etc.

### Virtual Environment Not Activating
```bash
# macOS/Linux: Check syntax
source venv/bin/activate

# Windows: Use correct script
.\venv\Scripts\Activate.ps1
```

### Missing Dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

### API Key Issues
- Keep `MOCK_LLM=true` in .env to use mock responses
- Get real keys from:
  - Google: https://aistudio.google.com/app/apikey
  - HuggingFace: https://huggingface.co/settings/tokens

---

## Running Tests

```bash
# Run all tests
PYTHONPATH=. python -m pytest tests/ -v

# Run specific test
PYTHONPATH=. python -m pytest tests/test_schema.py -v

# Run with coverage
PYTHONPATH=. python -m pytest tests/ --cov=agents --cov=utils
```

---

## Development Workflow

### Make Changes
```bash
# Edit files in your IDE
vim config.py  # or open in VS Code
```

### Test Your Changes
```bash
# Verify syntax
python3 -m py_compile agents/analyzer.py

# Run tests
PYTHONPATH=. python -m pytest tests/
```

### Push to GitHub
```bash
git add .
git commit -m "feat: Your feature description"
git push origin main
```

---

## Docker Setup (Optional)

If you prefer Docker:

```bash
# Build image
docker build -t devpulse .

# Run container
docker run -p 5050:5050 --env-file .env devpulse

# Visit http://localhost:5050
```

---

## Next Steps

1. **Explore the Dashboard** — Run analysis on sample data
2. **Try Draft Scoring** — Paste a markdown draft and get recommendations
3. **A/B Test Headlines** — Compare different titles
4. **Generate Reports** — Create GitHub issues for your content team
5. **Integrate Real Data** — Connect to your own Hacker News feeds

---

## Support

- 📖 [GitHub Repository](https://github.com/Vikas-Dr/Ai-Agent-Hackathon)
- 💬 Open an issue for bugs/features
- 🐍 Python docs: https://docs.python.org/3/
- ⚡ FastAPI: https://fastapi.tiangolo.com/

Happy coding! 🚀
