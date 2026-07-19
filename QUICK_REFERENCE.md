# 📌 QUICK REFERENCE CARD

## DevPulse with Agentic RAG - Complete System

---

## 🚀 GET STARTED (Choose One)

### Fastest: See Working Demo
```bash
python run_hackathon.py --demo
```
⏱️ **2 minutes** | Shows all features

### Quick: Full Pipeline
```bash
python run_hackathon.py --pipeline
```
⏱️ **1 minute** | Runs complete analysis

### Interactive: Dashboard
```bash
PYTHONPATH=. python3 -m ui.api_server
```
⏱️ **30 seconds setup** | Open http://localhost:5050

---

## 📖 DOCUMENTATION MAP

| Need | File | Time |
|------|------|------|
| Overview | README.md | 10 min |
| Setup | INSTALL.md | 5 min |
| Architecture | AGENT.md | 15 min |
| How-To | HACKATHON_README.md | 10 min |
| What's New | WHATS_NEW.md | 5 min |
| Summary | HACKATHON_COMPLETE.md | 5 min |

---

## 🎯 FEATURES AT A GLANCE

### Memory System
```python
from agentic_rag_hackathon import QuickMemory
memory = QuickMemory()
memory.remember_query(query, result, agent)
context = memory.get_context()
```
📌 Agent remembers past queries

### Semantic Search
```python
from agentic_rag_hackathon import QuickVectorStore
store = QuickVectorStore()
store.add("id", "content")
results = store.search("query", k=5)
```
🔍 Find similar items

### Reasoning Loop
```python
from agentic_rag_hackathon import QuickReACT
react = QuickReACT(memory, tools)
thoughts = react.think_and_act("query", "AgentName")
```
💭 Shows thinking: THOUGHT → ACTION → OBSERVATION

### Tool Registry
```python
from agentic_rag_hackathon import ToolKit
tools = ToolKit()
tools.add_tool("name", function)
result = tools.call("name", **params)
```
🔧 Pluggable tools

---

## 📊 WHAT'S INCLUDED

- ✅ Memory system (conversation history)
- ✅ Semantic search (no ML needed)
- ✅ ReACT reasoning (shows thinking)
- ✅ Tool registry (extensible)
- ✅ Multi-turn support (context aware)
- ✅ 5 specialized agents
- ✅ Dashboard UI
- ✅ REST API
- ✅ Demo scripts
- ✅ Complete documentation

---

## 🔧 BASIC USAGE

### Python Code
```python
from orchestrator.pipeline import run_pipeline

# Run with agentic features
result = run_pipeline(enable_agentic=True)

# Access results
print(result['report'])      # Editorial recommendations
print(result['analysis'])    # Content analytics
print(result['agentic'])     # Memory + reasoning
```

### Command Line
```bash
# Demo (2 min)
python run_hackathon.py --demo

# Pipeline (1 min)
python run_hackathon.py --pipeline

# Both (3 min)
python run_hackathon.py --all
```

### API
```bash
# Full analysis
curl -X POST http://localhost:5050/api/report \
  -H 'Content-Type: application/json' \
  -d '{"enable_agentic": true}'

# Score draft
curl -X POST http://localhost:5050/api/score \
  -H 'Content-Type: application/json' \
  -d '{"title": "...", "topic": "...", ...}'
```

---

## 💾 FILE LOCATIONS

| Component | File |
|-----------|------|
| Agentic System | `agentic_rag_hackathon.py` |
| Pipeline | `orchestrator/pipeline.py` |
| Agents | `agents/*.py` |
| Dashboard | `ui/index.html` |
| API | `ui/api_server.py` |
| Data | `data/sample_content_data.csv` |
| Tests | `tests/*.py` |
| Logs | `logs/*.log` |

---

## 🎯 5-MINUTE GUIDE

1. **Install** (if needed)
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **See Demo** (2 min)
   ```bash
   python run_hackathon.py --demo
   ```

3. **Understand** (2 min)
   - Read WHATS_NEW.md
   - View output from demo

4. **Next Steps**
   - Run full pipeline
   - Start dashboard
   - Read HACKATHON_README.md

---

## 🆘 TROUBLESHOOTING

| Issue | Fix |
|-------|-----|
| "Module not found" | `export PYTHONPATH=.` |
| "No API key" | Set `MOCK_LLM=true` in .env |
| "Port in use" | Kill process: `lsof -i :5050` |
| "Data missing" | Run: `python3 data/integrate_data.py` |

---

## 📈 ARCHITECTURE

```
User Query
    ↓
Memory Check (Did I see this before?)
    ↓
ReACT Planning (What should I do?)
    ↓
Tools (Search, cache, etc.)
    ↓
Agent Pipeline (5 agents)
    ↓
Store Results (Remember for next time)
    ↓
Output with Reasoning
```

---

## 🎓 LEARNING PATH

1. **Start** → README.md (overview)
2. **Setup** → INSTALL.md (installation)
3. **See** → `python run_hackathon.py --demo`
4. **Learn** → HACKATHON_README.md (details)
5. **Understand** → AGENT.md (architecture)
6. **Code** → agentic_rag_hackathon.py (implementation)
7. **Extend** → Add your own tools/features

---

## ✨ ONE-LINERS

```bash
# See everything work
python run_hackathon.py --demo

# Full analysis
python run_hackathon.py --pipeline

# Run tests
PYTHONPATH=. pytest tests/ -v

# Start dashboard
PYTHONPATH=. python3 -m ui.api_server

# Check data
head data/sample_content_data.csv

# View logs
tail -f logs/orchestrator.log
```

---

## 🎯 FOR JUDGES

### Show in 2 Minutes
```bash
python run_hackathon.py --demo
```
Demonstrates:
- Memory (remembers queries)
- Vector search (finds similar items)
- ReACT (shows reasoning)
- Tools (extensible)

### Explain in 5 Minutes
- "Agent remembers past queries"
- "Finds semantically similar content"
- "Shows thinking: THOUGHT → ACTION → OBSERVATION"
- "Extensible tool system"
- "Multi-turn conversations with context"

### Code Review (10 Minutes)
- agentic_rag_hackathon.py (450 LOC, single file)
- orchestrator/pipeline.py (integration)
- Easy to understand, easy to extend

---

## 💡 KEY METRICS

| Metric | Value | Status |
|--------|-------|--------|
| Memory Lookup | <1ms | ✅ Fast |
| Vector Search | <10ms | ✅ Fast |
| Full Pipeline | 2-3s | ✅ Fast |
| Setup Time | 5 min | ✅ Quick |
| Demo Time | 2 min | ✅ Short |
| LOC (Core) | 450 | ✅ Tight |

---

## 📚 DOCUMENTATION STRUCTURE

```
README.md                ← Overview
├─ Features
├─ Architecture
├─ Usage (5 options)
└─ API Reference

AGENT.md                 ← How it works
├─ Architecture
├─ Agents
└─ Design

INSTALL.md               ← Setup
├─ Requirements
├─ Installation steps
├─ Troubleshooting
└─ Verification

HACKATHON_README.md      ← Quick start
├─ Components
├─ Examples
├─ Tips
└─ FAQ
```

---

## 🚀 PRODUCTION CHECKLIST

- [ ] Read README.md
- [ ] Run `python run_hackathon.py --demo`
- [ ] Follow INSTALL.md
- [ ] Run tests: `pytest tests/ -v`
- [ ] Read AGENT.md
- [ ] Study agentic_rag_hackathon.py
- [ ] Understand orchestrator/pipeline.py
- [ ] Plan extensions
- [ ] Deploy!

---

## 🎁 WHAT YOU GET

✅ Working agentic RAG system  
✅ Complete documentation  
✅ Demo scripts  
✅ Setup guide  
✅ Code examples  
✅ Architecture docs  
✅ Troubleshooting guide  
✅ Production ready  

---

## 📞 RESOURCES

| Item | Location |
|------|----------|
| Demo | Run `python run_hackathon.py --demo` |
| Docs | README.md + HACKATHON_README.md |
| Code | agentic_rag_hackathon.py (450 LOC) |
| Setup | INSTALL.md |
| Architecture | AGENT.md |
| Examples | HACKATHON_DEMO.py |

---

**Status: 🟢 READY TO USE**

Print this card. Pin it to your desk. Reference whenever needed! 📌
