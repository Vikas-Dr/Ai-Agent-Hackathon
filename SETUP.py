"""
DevPulse Local Setup & Deployment Guide
Complete instructions for running DevPulse on your local machine
"""

# ==================== PREREQUISITES ====================
# 1. Python 3.10+
# 2. Git
# 3. Virtual environment tool (venv)
# 4. A text editor or IDE (VS Code, PyCharm, etc.)

# ==================== STEP 1: CLONE THE REPOSITORY ====================
# Open terminal and run:
# 
# git clone https://github.com/Vikas-Dr/Ai-Agent-Hackathon.git
# cd Ai-Agent-Hackathon

# ==================== STEP 2: CREATE VIRTUAL ENVIRONMENT ====================
# 
# macOS/Linux:
# python3 -m venv venv
# source venv/bin/activate
# 
# Windows (PowerShell):
# python -m venv venv
# .\venv\Scripts\Activate.ps1
# 
# Windows (Command Prompt):
# python -m venv venv
# venv\Scripts\activate.bat

# ==================== STEP 3: INSTALL DEPENDENCIES ====================
# 
# pip install --upgrade pip
# pip install -r requirements.txt

# ==================== STEP 4: SETUP ENVIRONMENT VARIABLES ====================
# Create a .env file in the project root and add:
# 
# LLM_PROVIDER=gemini
# LLM_MODEL=gemini-2.5-flash
# GOOGLE_API_KEY=your_google_api_key_here
# HF_TOKEN=your_huggingface_token_here
# MOCK_LLM=true
# DATA_PATH=data/sample_content_data.csv

# To get API keys:
# - Google API: https://aistudio.google.com/app/apikey
# - HuggingFace Token: https://huggingface.co/settings/tokens

# ==================== STEP 5: GENERATE DATA ====================
# 
# python data/integrate_data.py
# This fetches real Hacker News stories and generates sample_content_data.csv

# ==================== STEP 6: RUN THE DASHBOARD ====================
# 
# PYTHONPATH=. python ui/api_server.py
# 
# Then open: http://localhost:5050

# ==================== STEP 7: VERIFY INSTALLATION ====================
# 
# Run tests (optional):
# python -m pytest tests/ -v
# 
# Test the pipeline:
# PYTHONPATH=. python -c "
# from orchestrator import run_pipeline
# result = run_pipeline()
# print(f'✓ Analysis complete: {result[\"report\"][\"summary\"]}')
# "

print(__doc__)
