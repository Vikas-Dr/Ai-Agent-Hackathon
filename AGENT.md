# ContentPulse — AGENT.md

## Project
ContentPulse is a multi-agent AI system that turns content performance data into
editorial decisions: what to continue, what to stop, and what to create next —
including predicting how a draft will perform *before* it's published.

## Token Budget: 2,000,000 tokens (Codebenders IDE)
Build in strict module order. Do not move to the next module until the current
one is reviewed and working. Do not regenerate a whole module for a small fix —
request a targeted edit to the specific file instead.

| Phase | Module | Est. tokens | Notes |
|---|---|---|---|
| 1 | Plan / architecture doc | 20k | This file + data schema, no code yet |
| 2 | Data model + synthetic dataset | 80k | Pure Python/pandas, no LLM calls |
| 3 | Collector Agent | 100k | Load, clean, validate data |
| 4 | Analyzer Agent | 250k | Pandas aggregation + 1 LLM call for insight text |
| 5 | Predictor Agent | 350k | Core differentiator — most iteration happens here |
| 6 | Strategist Agent | 200k | Gap analysis logic |
| 7 | Report Agent | 200k | Combines Analyzer + Strategist output |
| 8 | Orchestrator | 150k | Wires agents together, agent trace logging |
| 9 | UI (dashboard, scorer form, report view) | 400k | Build after backend logic is proven |
| 10 | Integration + bug fixes | 200k | Reserve — don't spend this early |
| — | Buffer | 50k | Emergency reserve, do not pre-allocate |

**Rule: never prompt for more than one module at a time.**

---

## Build Order (follow exactly, in this sequence)

1. Data model + schema
2. Collector Agent
3. Analyzer Agent
4. Predictor Agent
5. Strategist Agent
6. Report Agent
7. Orchestrator (connects 2–6)
8. UI
9. Integration pass
10. Polish (only if tokens remain)

Do not skip ahead to UI or polish before the agents work end-to-end on the
command line / logs. A working backend with an ugly UI beats a pretty UI
with broken logic.

---

## Agent Roles

### 1. Collector Agent
- **Job**: Load and clean the published-content dataset (CSV/JSON).
- **Input**: raw file with title, url, topic, format, word_count, publish_date,
  views, engagement_rate, avg_time_on_page, conversions, search_rank.
- **Output**: a validated, normalized pandas DataFrame.
- **Does NOT**: call the LLM. This is pure data engineering.

### 2. Analyzer Agent
- **Job**: Aggregate performance by topic, format, length bucket, and time
  period; convert the aggregated stats into plain-English insights.
- **Input**: DataFrame from Collector Agent.
- **Output**: JSON — `{ insights: [string], top_topics: [...], top_formats: [...] }`
- **Rule**: Do all number-crunching in pandas. Only send the *already
  aggregated* summary stats to the LLM — never raw rows. This is the single
  biggest token-saver in the whole system.

### 3. Predictor Agent (core differentiator — prioritize this)
- **Job**: Score a new draft's likely performance before publishing.
- **Input**: draft title, topic, format, planned word count.
- **Process**: find the most similar historical content by topic/format/length,
  pass that comparison set to the LLM.
- **Output**: strict JSON — `{ predicted_score: 0-100, reasoning: string,
  suggestions: [string, string, string] }`
- **Rule**: `max_tokens` for this call should be 300–400, no more. If the
  dataset has too few comparable rows, say so explicitly instead of guessing.

### 4. Strategist Agent
- **Job**: Compare covered topics against a trending/competitor topic list
  (hardcoded or user-supplied for the demo) and flag content gaps.
- **Input**: Analyzer output + trending topic list.
- **Output**: JSON — `{ gaps: [string], reason: [string] }`

### 5. Report Agent
- **Job**: Combine Analyzer + Strategist output into a bi-weekly Content
  Intelligence Report.
- **Output**: JSON — `{ continue: [...], stop: [...], create_next: [...] }`
- **Does NOT**: call the LLM again if Analyzer/Strategist already produced
  usable text — just assemble and format it. Avoid a redundant third call.

### 6. Orchestrator
- **Job**: Run Collector → Analyzer → Strategist → Report in sequence for
  the report flow. Run Predictor independently, on-demand, for the draft
  scorer.
- **Must**: log which agent ran and what it decided at each step, so the
  multi-agent flow is visibly demonstrable in a live demo (not a black box).

---

## Global Rules for Every Prompt to the IDE

1. **Plan before you prompt** — never open a build prompt without knowing
   which module it targets and what its input/output contract is.
2. **One module per prompt** — never ask for "the whole agent system" in
   one shot. Layered prompts produce reliable code; giant prompts don't.
3. **Prompt precisely** — state the exact function/file, inputs, outputs,
   and libraries. "Build the Predictor Agent: input draft{title, topic,
   format, word_count}, output JSON {predicted_score, reasoning,
   suggestions}, using pandas for similarity lookup and one Claude API
   call" beats "make the predictor."
4. **Review before building on** — read what was generated before prompting
   the next module. Catching a wrong assumption at module 3 is cheap;
   catching it at module 9 is not.
5. **Edit, don't regenerate** — for small fixes, prompt for a targeted edit
   to the specific file/function. Never regenerate a whole module for a
   one-line fix.
6. **No LLM calls for math** — anything pandas can compute, pandas computes.
   The LLM is only for language (insights, predictions, report text).
7. **Mock before you wire up** — test orchestration and UI logic with
   hardcoded fake agent responses first; only swap in real LLM calls once
   the flow works end-to-end.
