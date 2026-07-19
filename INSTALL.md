# 📦 DevPulse Installation & Setup Guide

## System Requirements

- **Python**: 3.11+
- **OS**: macOS, Linux (Windows with WSL)
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 500MB for full installation + data

---

## 🚀 Quick Start (5 minutes)

### Step 1: Clone Repository
```bash
git clone <repo-url>
cd devpulse
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
cp .env.example .env
# Edit .env to add API keys if needed (optional for demo)
```

### Step 5: Load Data
```bash
PYTHONPATH=. python3 data/integrate_data.py
```

### Step 6: See It Working!
```bash
# Quick demo (2 minutes)
python run_hackathon.py --demo

# Or run full pipeline
python run_hackathon.py --pipeline
```

That's it! ✨

---

## 🏗️ Detailed Installation

### Prerequisites Check

```bash
# Check Python version
python3 --version
# Expected: Python 3.11.x or higher

# Check pip
pip --version

# Check git
git --version
```

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/devpulse.git

# Navigate to directory
cd devpulse

# Check structure
ls -la
# Should see: agents/, data/, llm/, orchestrator/, ui/, agentic_rag_hackathon.py, etc.
```

### Step 2: Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Verify activation (should show (venv) prefix in terminal)
```

### Step 3: Upgrade pip & Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify installation
python3 -c "import pandas; print('✓ pandas installed')"
python3 -c "import pydantic; print('✓ pydantic installed')"
python3 -c "import flask; print('✓ flask installed')"
```

### Step 4: Environment Configuration

```bash
# Copy example env
cp .env.example .env

# Edit .env (optional for demo, required for production)
nano .env  # or vim, or your editor

# Required for production:
# GOOGLE_API_KEY=your-key-here
# MOCK_LLM=false

# Recommended defaults (already in .env.example):
# MOCK_LLM=true              (no API calls, uses mock data)
# LLM_PROVIDER=gemini        (Gemini)
# LLM_MODEL=gemini-2.5-flash
```

### Step 5: Load Sample Data

```bash
# Set Python path
export PYTHONPATH=.

# Load data from Hacker News API (creates CSV with 200 articles)
python3 data/integrate_data.py

# Verify data loaded
ls -la data/sample_content_data.csv
# Should be ~100KB

wc -l data/sample_content_data.csv
# Should be 201 lines (200 rows + header)
```

### Step 6: Verify Installation

```bash
# Test imports
python3 << 'EOF'
from agents import CollectorAgent, AnalyzerAgent
from orchestrator.pipeline import run_pipeline
from agentic_rag_hackathon import create_agentic_context
print("✅ All imports successful!")
EOF
```

---

## 🧪 Testing Installation

### Quick Test (30 seconds)
```bash
# Run quick demo to verify everything works
python run_hackathon.py --demo

# Expected: Shows memory, vector search, ReACT reasoning in action
```

### Full Test (1-2 minutes)
```bash
# Run complete pipeline with agentic features
python run_hackathon.py --pipeline

# Expected: Full analysis with memory storage
```

### Run Test Suite (1-2 minutes)
```bash
# Run all unit tests
PYTHONPATH=. python3 -m pytest tests/ -v

# Expected: 30+ tests pass
# If tests fail, check error messages and requirements.txt versions
```

---

## 🎯 Common Installation Issues

### Issue 1: "command not found: python3"
**Solution**:
```bash
# Check Python installation
which python
which python3

# If not found, install Python:
# macOS: brew install python3
# Linux: apt-get install python3
# Windows: Download from python.org
```

### Issue 2: "ModuleNotFoundError" when importing
**Solution**:
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall requirements
pip install --force-reinstall -r requirements.txt

# Check installed packages
pip list | grep pandas
pip list | grep pydantic
```

### Issue 3: "GOOGLE_API_KEY missing but MOCK_LLM not set"
**Solution**:
```bash
# Edit .env
echo "MOCK_LLM=true" >> .env

# Or set environment variable
export MOCK_LLM=true

# Then try again
python run_hackathon.py --demo
```

### Issue 4: "No module named 'agentic_rag_hackathon'"
**Solution**:
```bash
# Make sure PYTHONPATH is set
export PYTHONPATH=.

# Or run with PYTHONPATH inline
PYTHONPATH=. python3 run_hackathon.py --demo

# Check file exists
ls -la agentic_rag_hackathon.py
```

### Issue 5: "permission denied: ./run_hackathon.py"
**Solution**:
```bash
# Make script executable
chmod +x run_hackathon.py

# Or run with python
python3 run_hackathon.py --demo
```

### Issue 6: "Address already in use" when starting server
**Solution**:
```bash
# Port 5050 is already in use, kill the process
lsof -i :5050
kill -9 <PID>

# Or use different port
PYTHONPATH=. python3 -m ui.api_server --port 5051
```

---

## 📊 Verify Full Setup

Run this comprehensive check:

```bash
#!/bin/bash
set -e

echo "🔍 Verifying DevPulse Installation..."
echo

# 1. Python version
echo "✓ Python version:"
python3 --version

# 2. Virtual environment
echo "✓ Virtual environment: $VIRTUAL_ENV"

# 3. Required packages
echo "✓ Checking packages..."
python3 << 'EOF'
packages = ['pandas', 'pydantic', 'flask', 'numpy', 'google_generativeai', 'openai']
for pkg in packages:
    try:
        __import__(pkg)
        print(f"  ✓ {pkg}")
    except ImportError:
        print(f"  ✗ {pkg} - MISSING!")
        raise
EOF

# 4. Data files
echo "✓ Data files:"
test -f data/sample_content_data.csv && echo "  ✓ sample_content_data.csv" || echo "  ✗ MISSING!"
test -f assets/data/hackernews_export.csv && echo "  ✓ hackernews_export.csv" || echo "  ✗ MISSING!"

# 5. Core modules
echo "✓ Core modules:"
ls -1 agents/*.py | head -3 | sed 's/^/  ✓ /'
ls -1 orchestrator/*.py | head -3 | sed 's/^/  ✓ /'

# 6. Agentic RAG module
echo "✓ Agentic RAG:"
test -f agentic_rag_hackathon.py && echo "  ✓ agentic_rag_hackathon.py" || echo "  ✗ MISSING!"

# 7. Run quick test
echo "✓ Running quick test..."
export PYTHONPATH=.
python3 -c "
from agentic_rag_hackathon import create_agentic_context
agentic = create_agentic_context()
print(f'  ✓ Agentic context created')
print(f'  ✓ Memory: {type(agentic[\"memory\"]).__name__}')
print(f'  ✓ Tools: {type(agentic[\"tools\"]).__name__}')
"

echo
echo "✅ All checks passed! Ready to use DevPulse"
```

Save this as `verify.sh` and run:
```bash
chmod +x verify.sh
./verify.sh
```

---

## 🚀 Next Steps After Installation

### Option 1: See It Working (Recommended)
```bash
# 2-minute demo showing all features
python run_hackathon.py --demo
```

### Option 2: Start the Dashboard
```bash
# Interactive web interface
PYTHONPATH=. python3 -m ui.api_server

# Then open: http://localhost:5050
```

### Option 3: Run Complete Pipeline
```bash
# Full analysis with all agents
python run_hackathon.py --pipeline
```

### Option 4: Run Tests
```bash
# Verify everything works
PYTHONPATH=. python3 -m pytest tests/ -v
```

---

## 📚 Configuration Reference

### Environment Variables (.env)

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| MOCK_LLM | No | true | Set to false for real LLM calls |
| GOOGLE_API_KEY | No | - | Gemini API key (if not using mock) |
| HF_TOKEN | No | - | Hugging Face token (if using Qwen) |
| LLM_PROVIDER | No | gemini | "gemini" or "huggingface" |
| LLM_MODEL | No | gemini-2.5-flash | LLM model name |
| DATA_PATH | No | data/sample_content_data.csv | Path to CSV data |
| LOGS_DIR | No | ./logs | Logging directory |
| ASSETS_DIR | No | ./assets | Assets directory |

### Example .env for Development
```bash
# Use mock LLM (no API calls needed)
MOCK_LLM=true

# If you want real LLM calls:
# MOCK_LLM=false
# GOOGLE_API_KEY=sk-xxx
# LLM_PROVIDER=gemini
# LLM_MODEL=gemini-2.5-flash

# Data paths
DATA_PATH=data/sample_content_data.csv
LOGS_DIR=./logs
ASSETS_DIR=./assets
```

---

## 🐳 Docker Installation (Optional)

If you prefer Docker:

```bash
# Build image
docker build -t devpulse .

# Run container
docker run -p 5050:5050 -v $(pwd):/app devpulse

# Visit: http://localhost:5050
```

**Dockerfile** (create if using Docker):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV MOCK_LLM=true

EXPOSE 5050

CMD ["python3", "-m", "ui.api_server"]
```

---

## 🔄 Updating Installation

### Update Dependencies
```bash
# Update all packages to latest versions
pip install --upgrade -r requirements.txt

# Or specific package
pip install --upgrade flask
```

### Update Code
```bash
# Pull latest from git
git pull origin main

# Install any new dependencies
pip install -r requirements.txt

# Reload data
PYTHONPATH=. python3 data/integrate_data.py
```

---

## 🗑️ Uninstall / Clean Up

### Remove Virtual Environment
```bash
# Deactivate first
deactivate

# Remove venv directory
rm -rf venv
```

### Clean Generated Files
```bash
# Remove logs
rm -rf logs/*.log

# Remove generated data
rm -f data/sample_content_data.csv
rm -f assets/data/hackernews_export.csv

# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Full Clean (Start Fresh)
```bash
# Remove everything generated
rm -rf venv logs/ __pycache__
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name ".DS_Store" -delete

# Now reinstall from scratch
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 data/integrate_data.py
```

---

## ✅ Installation Checklist

Use this to verify everything:

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (pip install -r requirements.txt)
- [ ] .env file configured
- [ ] Sample data loaded (data/integrate_data.py)
- [ ] Quick demo works (python run_hackathon.py --demo)
- [ ] Tests pass (pytest tests/ -v)
- [ ] Dashboard starts (python -m ui.api_server)
- [ ] Can access http://localhost:5050

---

## 📞 Support

If you encounter issues:

1. **Check Python version**: `python3 --version` (should be 3.11+)
2. **Verify venv activation**: (should see (venv) in prompt)
3. **Check dependencies**: `pip list | grep -E "pandas|pydantic|flask"`
4. **Check data**: `ls -la data/sample_content_data.csv`
5. **Run tests**: `PYTHONPATH=. pytest tests/ -v`
6. **Check logs**: `tail -f logs/orchestrator.log`
7. **Read TROUBLESHOOTING** section of README.md

---

## 🎉 Success!

Once installation is complete, you're ready to:

```bash
# See it working
python run_hackathon.py --demo

# Use the dashboard
PYTHONPATH=. python3 -m ui.api_server

# Run the pipeline
python run_hackathon.py --pipeline

# Integrate into your code
from orchestrator.pipeline import run_pipeline
result = run_pipeline(enable_agentic=True)
```

**Happy analyzing! 🚀**
