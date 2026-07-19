# 🔧 Agentic RAG Implementation Examples

This file shows **concrete code examples** of what each gap will look like after implementation.

---

## Gap 1: Memory System

### Before (Current DevPulse)
```python
# orchestrator/pipeline.py
def run_pipeline(data_path=None):
    """Every call is isolated — no context retained."""
    collector = CollectorAgent(data_path or str(DATA_PATH))
    collector_result, _, _ = collector.execute()  # Fresh start
    
    analyzer = AnalyzerAgent()
    analysis, _, _ = analyzer.execute(dataframe=collector_result["dataframe"])
    
    # If user asks another question, we start completely over
    return {"report": report.model_dump()}
```

### After (With Memory)
```python
from memory import MemoryManager

memory = MemoryManager()

def run_pipeline(data_path=None, user_id="default", session_id=None):
    """Agent now remembers prior queries and results."""
    
    # Check if we've seen this query before
    cached = memory.retrieve_exact(user_query="What topics are trending?")
    if cached and datetime.now() - cached['timestamp'] < timedelta(hours=1):
        return cached['result']  # Return cached result
    
    # Run pipeline as before
    collector = CollectorAgent(data_path or str(DATA_PATH))
    collector_result, collector_dur, _ = collector.execute()
    
    analyzer = AnalyzerAgent()
    analysis, analyzer_dur, _ = analyzer.execute(
        dataframe=collector_result["dataframe"]
    )
    
    # Store result in memory for future queries
    memory.store(
        user_id=user_id,
        session_id=session_id,
        query="What topics are trending?",
        agent="AnalyzerAgent",
        output=analysis.model_dump(),
        duration=analyzer_dur,
        metadata={"data_rows": len(collector_result["dataframe"])}
    )
    
    # Retrieve similar past insights to augment current output
    similar_insights = memory.retrieve_similar(
        query="topic trends",
        k=3,
        min_similarity=0.6
    )
    # → [insight_from_2_weeks_ago, insight_from_last_month, ...]
    
    return {
        "report": report.model_dump(),
        "augmented_context": similar_insights,
        "memory_hit": False
    }
```

### Memory Data Structure
```python
# memory/short_term_memory.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ConversationTurn:
    user_id: str
    session_id: str
    turn_number: int
    user_query: str
    agent_name: str
    agent_output: dict
    duration_seconds: float
    timestamp: datetime
    metadata: dict  # Extra context
    
class ShortTermMemory:
    def __init__(self, max_turns=50):
        self.turns: List[ConversationTurn] = []
        self.max_turns = max_turns
    
    def add_turn(self, turn: ConversationTurn):
        """Add to conversation history (FIFO if at max)."""
        if len(self.turns) >= self.max_turns:
            self.turns.pop(0)
        self.turns.append(turn)
    
    def get_recent(self, k=5) -> List[ConversationTurn]:
        """Last k turns in this session."""
        return self.turns[-k:]
    
    def get_context(self) -> str:
        """Summarize for LLM context."""
        if not self.turns:
            return "No prior conversation history."
        return "\n".join([
            f"- Q: {turn.user_query}\n  Agent: {turn.agent_name}"
            for turn in self.get_recent(3)
        ])

@dataclass
class KnowledgeItem:
    topic: str
    insight: str
    source_agent: str
    embedding: List[float]  # For semantic search
    created_at: datetime
    hit_count: int  # How many times retrieved
    
class LongTermMemory:
    def __init__(self, storage_path="./data/knowledge_base.db"):
        self.db = sqlite3.connect(storage_path)
        self.embedder = Embeddings()  # Use OpenAI or local
        self._init_db()
    
    def store_insight(self, topic: str, insight: str, agent: str):
        """Save learnings for future use."""
        embedding = self.embedder.embed(insight)
        item = KnowledgeItem(
            topic=topic,
            insight=insight,
            source_agent=agent,
            embedding=embedding,
            created_at=datetime.now(),
            hit_count=0
        )
        self.db.insert("knowledge", item.to_dict())
    
    def search(self, query: str, k=3) -> List[KnowledgeItem]:
        """Semantic search over stored insights."""
        query_embedding = self.embedder.embed(query)
        
        # Load all embeddings (or use vector DB)
        items = self.db.query("SELECT * FROM knowledge")
        
        # Compute cosine similarity
        scores = [
            (item, cosine_similarity(query_embedding, item['embedding']))
            for item in items
        ]
        
        # Return top k
        top_k = sorted(scores, key=lambda x: x[1], reverse=True)[:k]
        
        # Update hit counts
        for item, _ in top_k:
            self.db.update("knowledge", item['id'], {"hit_count": item['hit_count'] + 1})
        
        return [item for item, _ in top_k]
```

---

## Gap 2: ReACT Planning Module

### Before (Current DevPulse)
```python
# Hardcoded pipeline — no reasoning
collector = CollectorAgent()
analyzer = AnalyzerAgent()
strategist = StrategistAgent()
report = ReportAgent()
```

### After (With ReACT Planner)
```python
from planning import ReACTPlanner, Action

class AnalyzerAgentWithReasoning(AnalyzerAgent):
    def __init__(self, memory, tools):
        super().__init__()
        self.memory = memory
        self.tools = tools
        self.planner = ReACTPlanner(memory, tools)
    
    def run(self, dataframe, user_query="What insights do we have?"):
        """Use ReACT to reason about analysis approach."""
        
        # STEP 1: THOUGHT — What do we need to do?
        print("\n[THOUGHT]")
        print(f"Question: {user_query}")
        print("I need to:")
        print("  1. Check if we've analyzed this dataset before")
        print("  2. Run new analysis if data changed")
        print("  3. Compare with past insights to find patterns")
        
        # STEP 2: ACTION — Select tools
        print("\n[ACTION]")
        plan = self.planner.plan(
            query=user_query,
            data_shape=dataframe.shape,
            available_tools=["retrieve_analysis", "analyze_data", "search_memory"]
        )
        # → Action("retrieve_cached_analysis", {"data_hash": "abc123"})
        # → Action("run_groupby_aggregations", {"dataframe": df})
        # → Action("search_memory", {"topic": "insights", "k": 5})
        
        # STEP 3: OBSERVATION — Execute and observe
        print("\n[OBSERVATION]")
        cached_result = self.tools["retrieve_analysis"].execute(data_hash="abc123")
        if cached_result and not self._data_changed(cached_result['timestamp']):
            print(f"✓ Found cached analysis from {cached_result['timestamp']}")
            analysis = cached_result['analysis']
        else:
            print("✗ Cache miss or data changed, running fresh analysis...")
            analysis = self._run_aggregations(dataframe)
        
        past_insights = self.memory.search(query="content insights", k=5)
        print(f"✓ Retrieved {len(past_insights)} similar past insights")
        
        # STEP 4: REFLECTION — Did we get what we needed?
        print("\n[REFLECTION]")
        if len(analysis.insights) < 4:
            print("⚠ Low insight count, refining...")
            # Re-run with LLM to improve insights
            analysis = self._refine_with_llm(analysis, past_insights)
        else:
            print("✓ Insight quality sufficient")
        
        # STEP 5: ANSWER — Return result
        print("\n[ANSWER]")
        return analysis
```

### ReACT Planner Implementation
```python
# planning/react_planner.py
from typing import List
from dataclasses import dataclass

@dataclass
class Thought:
    text: str
    reasoning: str

@dataclass
class Action:
    tool_name: str
    parameters: dict
    description: str

@dataclass
class Observation:
    result: Any
    summary: str
    success: bool

@dataclass
class ReACTPlan:
    steps: List[tuple]  # (Thought, Action, Observation)
    final_answer: str
    reasoning_trace: List[str]

class ReACTPlanner:
    def __init__(self, memory, tools, llm_client=None):
        self.memory = memory
        self.tools = tools
        self.llm = llm_client
        self.max_steps = 5
        self.step_count = 0
    
    def plan(self, query: str, **context) -> ReACTPlan:
        """Generate and execute a ReACT plan."""
        steps = []
        reasoning_trace = [f"Planning for query: {query}"]
        
        for step_num in range(self.max_steps):
            # THOUGHT: What should we do?
            thought = self._generate_thought(
                query=query,
                prior_steps=steps,
                context=context
            )
            reasoning_trace.append(f"Step {step_num}: {thought.text}")
            
            # ACTION: Decide which tool to use
            action = self._select_action(
                thought=thought,
                available_tools=self.tools.keys(),
                context=context
            )
            reasoning_trace.append(f"  → Using tool: {action.tool_name}")
            
            # OBSERVATION: Execute and observe
            try:
                result = self.tools[action.tool_name].execute(**action.parameters)
                observation = Observation(
                    result=result,
                    summary=self._summarize_result(result),
                    success=True
                )
            except Exception as e:
                observation = Observation(
                    result=None,
                    summary=f"Tool failed: {str(e)}",
                    success=False
                )
            
            reasoning_trace.append(f"  ← Observation: {observation.summary}")
            steps.append((thought, action, observation))
            
            # Check if we're done
            if self._should_stop(observation, step_num):
                reasoning_trace.append(f"Stopping: {observation.summary}")
                break
        
        return ReACTPlan(
            steps=steps,
            final_answer=self._extract_answer(steps),
            reasoning_trace=reasoning_trace
        )
    
    def _generate_thought(self, query, prior_steps, context) -> Thought:
        """LLM generates next thought."""
        prompt = f"""
Given the query: {query}
Prior steps: {len(prior_steps)}
Current context: {context}

What should we do next? Think about:
1. What information do we have?
2. What do we still need?
3. Which tool would help?
"""
        response = self.llm.call(prompt)
        return Thought(text=response, reasoning=prompt)
    
    def _select_action(self, thought, available_tools, context) -> Action:
        """Choose which tool based on thought."""
        # Simple heuristic for demo; could use LLM
        if "cache" in thought.text.lower():
            tool = "retrieve_cached"
        elif "similar" in thought.text.lower():
            tool = "search_memory"
        elif "data" in thought.text.lower():
            tool = "run_analysis"
        else:
            tool = available_tools[0]
        
        return Action(
            tool_name=tool,
            parameters=context,
            description=thought.text
        )
    
    def _should_stop(self, observation, step_num) -> bool:
        """Decide if we have enough info to answer."""
        if not observation.success:
            return True  # Failed, stop
        if step_num >= self.max_steps - 1:
            return True  # Max steps reached
        return False
    
    def _extract_answer(self, steps) -> str:
        """Synthesize final answer from all observations."""
        return " ".join([obs.summary for _, _, obs in steps if obs.success])
```

---

## Gap 3: Vector Database (Semantic Search)

### Before (Current DevPulse)
```python
# agents/predictor.py - Exact matching only
def find_comparable_rows(dataframe, topic, format, audience):
    """Find similar historical rows (exact matching)."""
    # Level 1: exact match on topic + format + audience
    matches = dataframe[
        (dataframe['topic'] == topic) &
        (dataframe['format'] == format) &
        (dataframe['audience_segment'] == audience)
    ]
    
    if len(matches) < 3:
        # Level 2: relax to topic + format
        matches = dataframe[
            (dataframe['topic'] == topic) &
            (dataframe['format'] == format)
        ]
    
    if len(matches) < 3:
        # Level 3: topic only
        matches = dataframe[dataframe['topic'] == topic]
    
    return matches  # No semantic understanding
```

### After (With Vector Search)
```python
from retrieval import RAGRetriever, VectorStore

class PredictorAgentWithRetrieval(PredictorAgent):
    def __init__(self):
        super().__init__()
        self.vector_store = VectorStore()
        self.retriever = RAGRetriever(self.vector_store)
    
    def run(self, dataframe, title, topic, format, audience_segment, word_count):
        """Use semantic search to find relevant historical content."""
        
        # Create a search query combining all fields
        search_query = f"{topic} {format} {audience_segment} {title}"
        
        # Retrieve similar items using embeddings
        similar_items = self.retriever.retrieve(
            query=search_query,
            k=5,
            min_similarity=0.5,
            filters={"format": format}  # Can still filter
        )
        # Returns:
        # [
        #   {"score": 0.92, "item": Row(topic="API Design", ...)},
        #   {"score": 0.87, "item": Row(topic="REST APIs", ...)},
        #   {"score": 0.81, "item": Row(topic="Web Services", ...)},
        # ]
        
        # Use semantic matches instead of exact matches
        comparable_rows = [item["item"] for item in similar_items]
        
        if len(comparable_rows) >= 3:
            # Semantic match found good results
            summary = self._build_summary(comparable_rows)
        else:
            # Fallback to exact matching
            summary = self._build_summary(
                self._exact_match_fallback(dataframe, topic, format)
            )
        
        return self._predict_score(summary)
```

### Vector Store Implementation
```python
# retrieval/vector_store.py
from typing import List, Dict, Any
import numpy as np
from dataclasses import dataclass

@dataclass
class VectorItem:
    id: str
    text: str
    embedding: np.ndarray
    metadata: Dict[str, Any]
    created_at: datetime

class VectorStore:
    def __init__(self, embedding_model="all-MiniLM-L6-v2"):
        self.embedder = Embeddings(model=embedding_model)
        self.items: Dict[str, VectorItem] = {}
        self.index = None  # Could use FAISS or Pinecone
    
    def add(self, id: str, text: str, metadata: dict = None):
        """Add item to vector store."""
        embedding = self.embedder.embed(text)
        item = VectorItem(
            id=id,
            text=text,
            embedding=embedding,
            metadata=metadata or {},
            created_at=datetime.now()
        )
        self.items[id] = item
        # Rebuild index in production (use FAISS or Pinecone)
    
    def search(self, query: str, k: int = 5, min_similarity: float = 0.0) -> List[Dict]:
        """Search for similar items."""
        query_embedding = self.embedder.embed(query)
        
        # Compute similarity scores
        scores = []
        for item_id, item in self.items.items():
            sim = self._cosine_similarity(query_embedding, item.embedding)
            if sim >= min_similarity:
                scores.append({
                    "id": item_id,
                    "score": sim,
                    "text": item.text,
                    "metadata": item.metadata
                })
        
        # Return top k
        return sorted(scores, key=lambda x: x["score"], reverse=True)[:k]
    
    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Cosine similarity between two vectors."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

class RAGRetriever:
    def __init__(self, vector_store: VectorStore):
        self.store = vector_store
    
    def retrieve(self, query: str, k: int = 5, min_similarity: float = 0.5, 
                 filters: dict = None) -> List[Dict]:
        """Retrieve with optional filtering."""
        results = self.store.search(query, k=k*2, min_similarity=min_similarity)
        
        # Apply filters if provided
        if filters:
            results = [r for r in results if self._matches_filters(r, filters)]
        
        return results[:k]
    
    @staticmethod
    def _matches_filters(item: dict, filters: dict) -> bool:
        """Check if item matches all filters."""
        for key, value in filters.items():
            if item["metadata"].get(key) != value:
                return False
        return True
```

---

## Gap 4: Tool Interface (Extensible)

### Before (Current DevPulse)
```python
# Tools buried in agents, hard to add new ones
class AnalyzerAgent:
    def run(self, dataframe):
        # Tool logic hardcoded here
        if cache_exists():
            cached = load_cache()
        # ...
```

### After (With Tool Registry)
```python
from tools import Tool, ToolRegistry

# Define tools
class CacheTool(Tool):
    name = "cache_lookup"
    description = "Retrieve cached analysis results"
    
    def execute(self, key: str) -> Optional[Dict]:
        # Implementation
        return cache.get(key)

class WebSearchTool(Tool):
    name = "web_search"
    description = "Search the web for trends"
    
    def execute(self, query: str, k: int = 5) -> List[str]:
        # Use SerpAPI or similar
        return search_api.search(query, k)

class DatabaseTool(Tool):
    name = "db_query"
    description = "Query database"
    
    def execute(self, sql: str) -> List[Dict]:
        # Execute SQL query
        return db.execute(sql)

# Register tools
tools = ToolRegistry()
tools.register(CacheTool())
tools.register(WebSearchTool())
tools.register(DatabaseTool())

# Use in agent
class AgentWithTools(BaseAgent):
    def __init__(self, tools: ToolRegistry):
        super().__init__()
        self.tools = tools
    
    def run(self, **kwargs):
        # Call any registered tool
        cached = self.call_tool("cache_lookup", key="analysis_v1")
        if cached:
            return cached
        
        trends = self.call_tool("web_search", query="API trends 2024")
        results = self.call_tool("db_query", sql="SELECT * FROM content")
        
        # Combine and return
        return combine(cached, trends, results)
    
    def call_tool(self, tool_name: str, **kwargs):
        """Call a registered tool."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        return self.tools[tool_name].execute(**kwargs)
```

### Tool Registry Implementation
```python
# tools/tool_registry.py
from typing import Dict, List, Callable
from abc import ABC, abstractmethod

class Parameter:
    def __init__(self, name: str, type_: str, required: bool = True, 
                 description: str = ""):
        self.name = name
        self.type = type_
        self.required = required
        self.description = description

class Tool(ABC):
    name: str
    description: str
    parameters: List[Parameter]
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool."""
        pass
    
    def validate_params(self, **kwargs) -> bool:
        """Check if required parameters provided."""
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                raise ValueError(f"Missing required parameter: {param.name}")
        return True

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.call_history: List[Dict] = []
    
    def register(self, tool: Tool):
        """Register a new tool."""
        if tool.name in self.tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self.tools[tool.name] = tool
        print(f"✓ Registered tool: {tool.name}")
    
    def get(self, name: str) -> Tool:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict]:
        """List all available tools."""
        return [
            {
                "name": name,
                "description": tool.description,
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type,
                        "required": p.required,
                        "description": p.description
                    }
                    for p in tool.parameters
                ]
            }
            for name, tool in self.tools.items()
        ]
    
    def call(self, tool_name: str, **kwargs):
        """Call a tool and log the call."""
        tool = self.get(tool_name)
        if not tool:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool.validate_params(**kwargs)
        
        # Log the call
        self.call_history.append({
            "tool": tool_name,
            "params": kwargs,
            "timestamp": datetime.now()
        })
        
        # Execute
        result = tool.execute(**kwargs)
        return result
    
    def __getitem__(self, name: str) -> Tool:
        """Enable dict-like access."""
        return self.get(name)
```

---

## Quick Reference: Implementation Order

1. **Memory System** → Short-term conversation + long-term knowledge base
2. **Tool Interface** → Abstract Tool + Registry
3. **ReACT Planner** → Multi-step reasoning loops
4. **Vector Store** → Semantic search with embeddings
5. **Adaptive Loops** → Feedback-based refinement
6. **NLU / Router** → Intent-based routing (optional)

---

**Next Step**: Pick a gap, verify you understand the code, and I'll build it! 🚀
