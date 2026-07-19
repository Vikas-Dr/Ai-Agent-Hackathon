# Quick Start Guide

## 5-Minute Setup

### Prerequisites
- Python 3.9+
- pip or conda
- Virtual environment (recommended)

### Step 1: Setup Environment

```bash
# Clone or navigate to project
cd devpulse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# Required: At least one LLM provider (OpenAI, Gemini, or Claude)
```

### Step 3: Run the Dashboard

```bash
# Start Flask API server
python ui/api_server.py

# Dashboard will be available at:
# http://localhost:5000
```

## Using the Dashboard

### 1. **Dashboard Tab**
- Click "Run Analysis" to analyze content
- View KPI metrics with trend indicators (↑/↓/→)
- See 2x2 Content Strategy Matrix
- Review quarterly trends and insights

### 2. **Draft Scorer Tab**
- Enter article title, topic, format, audience
- Input word count
- Optionally paste markdown or upload diagram
- Get performance prediction (0-100 score)
- See comparable historical content

### 3. **A/B Tester Tab**
- Test 3 headline variants
- Compare 2 code hooks
- Get engagement scores
- See combined recommendation

### 4. **Custom Dataset Tab**
- Upload your own CSV file
- Run analysis on custom metrics
- Export insights

### 5. **Strategy Report Tab**
- Generate editorial recommendations
- View Continue/Stop/Create items
- Export as PDF, GitHub issues, or summary
- Copy recommendations to clipboard

### 6. **Data Table Tab**
- Browse full dataset
- Sort by any column
- Filter and export

## API Endpoints (for developers)

```bash
# Health check
curl http://localhost:5000/api/health

# Run analysis
curl -X POST http://localhost:5000/api/report

# Get configuration (topics, formats, audiences)
curl http://localhost:5000/api/topics
curl http://localhost:5000/api/formats
curl http://localhost:5000/api/audiences

# Score a draft
curl -X POST http://localhost:5000/api/score \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Building REST APIs",
    "topic": "API Design",
    "format": "Tutorial",
    "audience": "Backend Developers",
    "word_count": 1500
  }'
```

## Demo Scripts

### Simple Demo (no external APIs)
```bash
python simple_demo.py
```
Uses mock data to demonstrate core features.

### Full Hackathon Demo
```bash
python run_hackathon.py
```
Runs complete pipeline with real LLM agents.

### Lightweight Demo
```bash
python demo_no_deps.py
```
Minimal dependencies, fast execution.

## Troubleshooting

### Port Already in Use
```bash
# Change port in config.py or run on different port
python ui/api_server.py --port 5001
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### API Key Issues
- Check `.env` file exists
- Verify API key format
- Test key with: `python -c "import config; print(config.OPENAI_API_KEY)"`

### Dashboard Not Loading
- Check browser console for JS errors
- Verify Flask server is running: `curl http://localhost:5000`
- Check logs: `tail -f logs/api_server.log`

## Next Steps

1. **Read ARCHITECTURE.md** - Understand system design
2. **Check README.md** - Full project documentation
3. **Explore INSTALL.md** - Detailed installation steps
4. **Try demo scripts** - Test functionality
5. **Review agent code** - Learn agent patterns

## Environment Variables

Key variables in `.env`:

```
# LLM Provider (choose at least one)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
CLAUDE_API_KEY=...

# Flask Server
FLASK_PORT=5000
FLASK_DEBUG=True

# Database
DATABASE_URL=sqlite:///devpulse.db

# Vector Search
CHROMA_PATH=./chroma_db
```

## Command Cheat Sheet

```bash
# Run dashboard
python ui/api_server.py

# Run demo
python simple_demo.py

# Check logs
tail -f logs/api_server.log

# Install deps
pip install -r requirements.txt

# Activate venv
source venv/bin/activate

# Run tests
pytest tests/

# Format code
black .

# Type check
mypy .
```

## Getting Help

- **API Issues**: Check `/logs/api_server.log`
- **Data Issues**: Review `/data/sample_content_data.csv`
- **Agent Errors**: Enable DEBUG in `.env`
- **UI Problems**: Open browser DevTools (F12)

---

**Need more details?** See INSTALL.md for comprehensive setup instructions.
