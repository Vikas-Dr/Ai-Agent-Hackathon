DEVPULSE - QUICK START CARD

FIRST TIME SETUP (Do once)

1. Clone repository
git clone <repo-url>
cd devpulse

2. Create environment
python3 -m venv venv
source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Load data
export PYTHONPATH=.
python3 data/integrate_data.py

5. Run demo
python run_hackathon.py --demo

Time: 10-15 minutes total

---

RUNNING DEVPULSE (Every time)

Before running: Activate venv
source venv/bin/activate

Option 1: Quick Demo (2 minutes)
python run_hackathon.py --demo

Option 2: Full Pipeline (1 minute)
python run_hackathon.py --pipeline

Option 3: Interactive Dashboard
export PYTHONPATH=.
python3 -m ui.api_server
Then visit: http://localhost:5050

Option 4: Both Demo and Pipeline
python run_hackathon.py --all

Option 5: Run Tests
export PYTHONPATH=.
python3 -m pytest tests/ -v

---

COMMON COMMANDS

View logs:
tail -f logs/orchestrator.log

Stop dashboard:
Press Ctrl+C

Reload data:
python3 data/integrate_data.py

Check Python version:
python3 --version

List installed packages:
pip list

---

IF SOMETHING FAILS

Error: "module not found"
Fix: export PYTHONPATH=.

Error: "venv not activated"
Fix: source venv/bin/activate

Error: "port 5050 in use"
Fix: kill -9 $(lsof -t -i :5050)

Error: "data file missing"
Fix: python3 data/integrate_data.py

Error: "test failures"
Fix: pip install --force-reinstall -r requirements.txt

---

FILE LOCATIONS

Data:
data/sample_content_data.csv

Logs:
logs/orchestrator.log
logs/agents.log

Configuration:
.env (create from .env.example)

Dashboard:
ui/index.html (opened at http://localhost:5050)

---

KEY FILES

README.md - Complete documentation
INSTALL.md - Detailed setup guide
AGENT.md - Architecture overview
STEP_BY_STEP_GUIDE.md - This guide with more detail

---

TIME ESTIMATES

Setup (first time): 10-15 minutes
Quick demo: 2 minutes
Full pipeline: 1 minute
Dashboard startup: 30 seconds
Tests: 2 minutes

---

NEXT STEPS

1. Follow "FIRST TIME SETUP" above
2. Run "Option 1: Quick Demo"
3. Read README.md for features
4. Try "Option 3: Interactive Dashboard"
5. Explore the code

---

SUPPORT

Full setup details: Read STEP_BY_STEP_GUIDE.md
Architecture details: Read AGENT.md
Features overview: Read README.md
Troubleshooting: Read INSTALL.md

---

Status: Ready to start!

Follow the steps above and you'll be running DevPulse in 15 minutes.
