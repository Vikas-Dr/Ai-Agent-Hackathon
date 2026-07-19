DEVPULSE - STEP-BY-STEP SETUP AND RUN GUIDE

PART 1: INITIAL SETUP (First Time Only)

Step 1: Clone the Repository

Open terminal and run:
git clone <repo-url>
cd devpulse

Expected output: You should see folder structure with agents/, data/, llm/, etc.

Step 2: Create Virtual Environment

Run:
python3 -m venv venv

Expected output: venv folder created

Step 3: Activate Virtual Environment

On macOS/Linux:
source venv/bin/activate

On Windows:
venv\Scripts\activate

Expected output: (venv) should appear in terminal prompt

Step 4: Verify Python Version

Run:
python3 --version

Expected output: Python 3.11.x or higher

Step 5: Upgrade pip

Run:
pip install --upgrade pip

Expected output: Successfully installed or already satisfied

Step 6: Install Dependencies

Run:
pip install -r requirements.txt

Expected output: Successfully installed pandas, pydantic, flask, etc.
Time: 2-5 minutes depending on internet speed

Step 7: Setup Environment File

Run:
cp .env.example .env

Expected output: .env file created in root directory

Step 8: Load Sample Data

Run:
export PYTHONPATH=.
python3 data/integrate_data.py

Expected output: 
- Data loading...
- Successfully loaded 200 articles
- CSV file created: data/sample_content_data.csv

Step 9: Verify Installation

Run:
python3 << 'EOF'
from agents import CollectorAgent
from orchestrator.pipeline import run_pipeline
from agentic_rag_hackathon import create_agentic_context
print("SUCCESS: All imports working!")
EOF

Expected output: SUCCESS: All imports working!

Setup Complete! You can now run DevPulse.

---

PART 2: RUNNING DEVPULSE

Option A: Quick Demo (Recommended First Time)

Step 1: Run the demo

python run_hackathon.py --demo

Step 2: Watch the output

You will see:
- Memory system demonstration
- Vector search examples
- ReACT reasoning loop
- Full agentic system integration

Step 3: Wait for completion

Time: 2 minutes
Status: Complete when you see final summary

---

Option B: Full Pipeline Execution

Step 1: Set Python path

export PYTHONPATH=.

Step 2: Run full pipeline

python3 run_hackathon.py --pipeline

Step 3: Watch execution

You will see:
- Stage 1: Data collection (0.05s)
- Stage 2: Analysis (0.01s)
- Stage 3: Gap identification (0.01s)
- Stage 4: Report generation (0.01s)

Step 4: View results

Report shows:
- Continue items (recommended topics)
- Stop items (topics to pause)
- Create next (new opportunities)
- Memory statistics
- Reasoning traces

Time: 1-2 minutes

---

Option C: Interactive Dashboard

Step 1: Start the server

export PYTHONPATH=.
python3 -m ui.api_server

Step 2: Wait for server to start

Expected output:
Running on http://127.0.0.1:5050

Step 3: Open in browser

Visit: http://localhost:5050

Step 4: Use the dashboard

Tab 1 - Dashboard:
- Click "Run Analysis"
- View metrics and charts
- See execution trace

Tab 2 - Draft Scorer:
- Enter title, topic, format, audience
- Click "Score This Draft"
- View prediction and suggestions

Tab 3 - Strategy Report:
- Click "Generate Report"
- View continue/stop/create items

Tab 4 - Chat:
- Have multi-turn conversation
- View memory of past queries
- See reasoning traces

Step 5: Stop the server

Press: Ctrl+C in terminal

---

Option D: Command-Line Usage

Step 1: Create Python script

Create file: test_devpulse.py

Add this code:
from orchestrator.pipeline import run_pipeline
import json

result = run_pipeline(enable_agentic=True)

print("Report Summary:")
print(result['report']['summary'])

print("\nAgentic Features:")
print(f"Memory size: {result['agentic']['memory_size']}")
print(f"Insights stored: {result['agentic']['insights_stored']}")
print(f"Vector items: {result['agentic']['vector_items']}")

Step 2: Run the script

export PYTHONPATH=.
python3 test_devpulse.py

Step 3: View output

You will see:
- Report summary
- Memory statistics
- Analysis results

---

Option E: Python Interactive Mode

Step 1: Open Python shell

export PYTHONPATH=.
python3

Step 2: Import modules

from orchestrator.pipeline import run_pipeline
from agentic_rag_hackathon import create_agentic_context

Step 3: Create agentic context

agentic = create_agentic_context()

Step 4: Explore memory system

agentic["memory"].remember_query(
    query="What topics are trending?",
    result={"insights": ["API Design +20%"]},
    agent="AnalyzerAgent"
)

Step 5: Retrieve context

print(agentic["memory"].get_context())

Step 6: Run pipeline

result = run_pipeline(enable_agentic=True)

Step 7: View results

print(result['report'])

Step 8: Exit

exit()

---

PART 3: VERIFY EVERYTHING WORKS

Run Tests

Step 1: Run all tests

export PYTHONPATH=.
python3 -m pytest tests/ -v

Step 2: Check results

Expected output: 30 passed in X.XXs

If all pass: Everything is working correctly

Check Logs

Step 1: View log files

ls -la logs/

Step 2: Check pipeline trace

cat logs/pipeline_trace.json

---

PART 4: COMMON TASKS

Task 1: Score a Draft

Code:
from orchestrator.scorer import score_draft

result = score_draft(
    title="Building APIs with Python",
    topic="API Design",
    fmt="tutorial",
    audience_segment="backend",
    word_count=1500
)

print(f"Score: {result['prediction']['predicted_score']}")
print(f"Suggestions: {result['prediction']['suggestions']}")

Task 2: Generate Report

Code:
from orchestrator.pipeline import run_pipeline

result = run_pipeline(enable_agentic=True)
print(result['report']['summary'])

for item in result['report']['continue_items']:
    print(f"Continue: {item.topic} - {item.reason}")

for item in result['report']['stop_items']:
    print(f"Stop: {item.topic} - {item.reason}")

Task 3: Use Memory System

Code:
from agentic_rag_hackathon import QuickMemory

memory = QuickMemory()

# Store query
memory.remember_query(
    query="What topics are trending?",
    result={"trends": ["API Design", "DevOps"]},
    agent="AnalyzerAgent"
)

# Recall
print(memory.get_context())

# Store insight
memory.store_insight("trends", "API Design up 20%")

# Retrieve
insights = memory.recall_similar("trends")

Task 4: Semantic Search

Code:
from agentic_rag_hackathon import QuickVectorStore

store = QuickVectorStore()

# Add content
store.add("api_guide", "Building REST APIs")
store.add("sdk_guide", "Creating SDKs")

# Search
results = store.search("API development", k=2)
for r in results:
    print(f"{r['id']}: {r['content']} (score: {r['score']})")

---

PART 5: TROUBLESHOOTING

Problem: "command not found: python3"

Solution 1: Check installation
which python3

Solution 2: Use python instead
python --version

Solution 3: Install Python 3.11+

Problem: "ModuleNotFoundError: No module named 'pandas'"

Solution 1: Verify venv is activated
(venv) should show in prompt

Solution 2: Reinstall dependencies
pip install -r requirements.txt

Problem: "PYTHONPATH not set"

Solution 1: Set it in terminal
export PYTHONPATH=.

Solution 2: Or run inline
PYTHONPATH=. python3 script.py

Problem: "Port 5050 already in use"

Solution 1: Kill the process
lsof -i :5050
kill -9 <PID>

Solution 2: Use different port
python3 -m ui.api_server --port 5051

Problem: "No such file or directory: data/sample_content_data.csv"

Solution 1: Load data
python3 data/integrate_data.py

Solution 2: Verify location
ls -la data/

Problem: "Tests are failing"

Solution 1: Check Python version
python3 --version (must be 3.11+)

Solution 2: Check dependencies
pip list | grep pytest

Solution 3: Reinstall
pip install --force-reinstall -r requirements.txt

---

PART 6: DAILY WORKFLOW

Morning: Check Analytics

Step 1: Run dashboard
export PYTHONPATH=.
python3 -m ui.api_server

Step 2: Visit http://localhost:5050

Step 3: Click "Run Analysis" on Dashboard tab

Step 4: Review metrics, insights, and trends

During Day: Score Drafts

Step 1: Go to "Draft Scorer" tab

Step 2: Enter draft information

Step 3: Click "Score This Draft"

Step 4: Review prediction and suggestions

Afternoon: Generate Strategy Report

Step 1: Go to "Strategy Report" tab

Step 2: Click "Generate Report"

Step 3: Review Continue/Stop/Create recommendations

Evening: Export Results

Code:
from orchestrator.pipeline import run_pipeline
import json

result = run_pipeline(enable_agentic=True)

with open('report.json', 'w') as f:
    json.dump(result['report'], f, indent=2)

print("Report exported to report.json")

---

PART 7: QUICK REFERENCE

Most Common Commands

Quick demo:
python run_hackathon.py --demo

Full pipeline:
python run_hackathon.py --pipeline

Both:
python run_hackathon.py --all

Start dashboard:
export PYTHONPATH=.
python3 -m ui.api_server

Run tests:
export PYTHONPATH=.
python3 -m pytest tests/ -v

Load data:
export PYTHONPATH=.
python3 data/integrate_data.py

Score draft:
python3 -c "from orchestrator.scorer import score_draft; print(score_draft('title', 'API Design', 'blog', 'backend', 1500))"

View logs:
tail -f logs/orchestrator.log

---

SUMMARY

Setup (First Time):
1. Clone repo
2. Create venv
3. Activate venv
4. Install requirements
5. Load data
6. Verify installation
Time: 10 minutes

Running (Every Time):
Option A: python run_hackathon.py --demo (2 min)
Option B: python run_hackathon.py --pipeline (1 min)
Option C: python3 -m ui.api_server (interactive)
Option D: Create Python script (customized)

All options work. Choose based on your need.

Questions?

Read INSTALL.md for detailed setup
Read HACKATHON_README.md for features
Read README.md for complete reference

Status: Ready to run!
