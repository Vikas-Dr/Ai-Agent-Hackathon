# How to Run: Generate Sample Data

## Quick Command

```bash
PYTHONPATH=. python data/integrate_data.py
```

---

## Step-by-Step Terminal Guide

### 1. Open Terminal/Command Prompt

**macOS/Linux:**
- Press `Cmd + Space`, type `terminal`, press Enter
- OR open Applications → Utilities → Terminal

**Windows:**
- Press `Win + R`, type `cmd`, press Enter
- OR search "Command Prompt" or "PowerShell" in Start menu

### 2. Navigate to Project Directory

```bash
cd path/to/Ai-Agent-Hackathon
```

**Example:**
```bash
# macOS/Linux
cd ~/projects/Ai-Agent-Hackathon

# Windows
cd C:\Users\YourName\projects\Ai-Agent-Hackathon
```

### 3. Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

Expected output:
```
(venv) user@machine Ai-Agent-Hackathon %
```
Notice `(venv)` appears before the prompt — this means the virtual environment is active.

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

Expected output:
```
(venv) C:\Users\YourName\projects\Ai-Agent-Hackathon>
```

### 4. Run the Data Generation Script

```bash
PYTHONPATH=. python data/integrate_data.py
```

**What happens:**
- Script fetches real Hacker News stories
- Processes and cleans data
- Adds DevRel metrics (API signups, GitHub stars growth)
- Creates `data/sample_content_data.csv`
- Shows progress with timestamps

**Expected output:**
```
[2024-01-15 10:30:45] Starting HN data integration...
[2024-01-15 10:30:46] Fetching stories from Hacker News API...
[2024-01-15 10:30:52] Downloaded 100 stories
[2024-01-15 10:30:53] Processing stories...
[2024-01-15 10:30:54] ✓ Generated 95 valid rows
[2024-01-15 10:30:55] Writing to data/sample_content_data.csv...
[2024-01-15 10:30:56] ✓ Data integration complete!
```

---

## Troubleshooting

### ❌ Command Not Found: python

**Problem:** `python: command not found`

**Solution:**
```bash
# Try python3 instead
PYTHONPATH=. python3 data/integrate_data.py

# Or check Python is installed
python --version
python3 --version
```

---

### ❌ ModuleNotFoundError

**Problem:** `ModuleNotFoundError: No module named 'pydantic'`

**Solution:** Virtual environment not activated or dependencies not installed

```bash
# Make sure venv is active (should see (venv) in prompt)
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Try again
PYTHONPATH=. python data/integrate_data.py
```

---

### ❌ PYTHONPATH Error

**Problem:** `ModuleNotFoundError: No module named 'config'`

**Solution:** PYTHONPATH not set correctly

```bash
# Correct way (period = current directory)
PYTHONPATH=. python data/integrate_data.py

# NOT this (common mistake)
PYTHONPATH=data python data/integrate_data.py
```

---

### ❌ File Not Found

**Problem:** `FileNotFoundError: [Errno 2] No such file or directory: 'data/integrate_data.py'`

**Solution:** Not in correct directory

```bash
# Check current directory
pwd                    # macOS/Linux
cd                     # Windows

# Should show something ending with 'Ai-Agent-Hackathon'

# If not, navigate there:
cd path/to/Ai-Agent-Hackathon
```

---

### ❌ Network Error (No Internet)

**Problem:** `URLError` or `ConnectionError` when fetching Hacker News

**Solution:** Use mock data

1. Skip data generation for now
2. The project includes mock data in `config.py`
3. Set `MOCK_LLM=true` in `.env`
4. Run the dashboard with sample data

```bash
PYTHONPATH=. python ui/api_server.py
```

---

## What Gets Created

After running `python data/integrate_data.py`, you'll have:

```
data/
├── sample_content_data.csv    ← New file with 100+ rows
├── schema.py
├── integrate_data.py
└── collector.py
```

### CSV Columns Include:
- `title` — Article title
- `url` — Story URL
- `score` — HN upvotes
- `comments` — Comment count
- `topic` — Classified topic (API Design, Authentication, etc.)
- `format` — Content format (blog, tutorial, etc.)
- `audience_segment` — Target audience (backend, frontend, etc.)
- `engagement_rate` — Normalized engagement metric
- `conversions` — Estimated API signups
- `github_stars_growth` — GitHub stars growth estimate
- `api_signups` — Estimated developer signups
- `code_to_text_ratio` — Code density in content

---

## Alternative: Skip Data Generation

If you don't want to fetch HN data, you can:

1. **Use mock mode** (no real data needed):
   ```bash
   # Edit .env
   MOCK_LLM=true
   ```

2. **Start dashboard directly**:
   ```bash
   PYTHONPATH=. python ui/api_server.py
   ```

3. **Use sample CSV** if it already exists from a prior run

---

## Windows-Specific Notes

### PowerShell Execution Policy Error

If you get: `cannot be loaded because running scripts is disabled`

```powershell
# Allow execution for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate venv
.\venv\Scripts\Activate.ps1

# Then run data generation
PYTHONPATH=. python data/integrate_data.py
```

### Environment Variable on Windows

Windows doesn't use `PYTHONPATH=.` syntax. Use one of:

```cmd
# Option 1: Set environment variable then run
set PYTHONPATH=.
python data/integrate_data.py

# Option 2: Use this one-liner (PowerShell)
$env:PYTHONPATH = "."; python data/integrate_data.py

# Option 3: Change to Python path directly
cd data
python -c "import sys; sys.path.insert(0, '..'); exec(open('integrate_data.py').read())"
```

---

## Full Terminal Session Example

### macOS/Linux:
```bash
# 1. Open terminal
# 2. Navigate to project
$ cd ~/projects/Ai-Agent-Hackathon

# 3. Activate venv
$ source venv/bin/activate
(venv) user@machine Ai-Agent-Hackathon %

# 4. Generate data
(venv) user@machine Ai-Agent-Hackathon % PYTHONPATH=. python data/integrate_data.py
[2024-01-15 10:30:45] ✓ Data integration complete!

# 5. Verify file created
(venv) user@machine Ai-Agent-Hackathon % ls -lh data/sample_content_data.csv
-rw-r--r--  1 user  staff   48K Jan 15 10:30 data/sample_content_data.csv

# 6. Start dashboard
(venv) user@machine Ai-Agent-Hackathon % PYTHONPATH=. python ui/api_server.py
 * Running on http://127.0.0.1:5050
```

### Windows (PowerShell):
```powershell
# 1. Open PowerShell
# 2. Navigate to project
PS C:\> cd C:\Users\YourName\projects\Ai-Agent-Hackathon

# 3. Activate venv
PS C:\...> .\venv\Scripts\Activate.ps1
(venv) PS C:\...>

# 4. Generate data
(venv) PS C:\...> $env:PYTHONPATH = "."; python data/integrate_data.py
[2024-01-15 10:30:45] ✓ Data integration complete!

# 5. Verify file created
(venv) PS C:\...> ls data/sample_content_data.csv

# 6. Start dashboard
(venv) PS C:\...> $env:PYTHONPATH = "."; python ui/api_server.py
 * Running on http://127.0.0.1:5050
```

---

## Next: Start the Dashboard

After data generation completes, run:

```bash
PYTHONPATH=. python ui/api_server.py
```

Then open: **http://localhost:5050**

---

## Quick Checklist

- [ ] Terminal/Command Prompt opened
- [ ] Navigated to `Ai-Agent-Hackathon` directory
- [ ] Virtual environment activated (see `(venv)` in prompt)
- [ ] Run: `PYTHONPATH=. python data/integrate_data.py`
- [ ] Wait for "✓ Data integration complete!"
- [ ] Check `data/sample_content_data.csv` was created
- [ ] Run: `PYTHONPATH=. python ui/api_server.py`
- [ ] Open browser to http://localhost:5050

✅ Done! DevPulse is running locally.
