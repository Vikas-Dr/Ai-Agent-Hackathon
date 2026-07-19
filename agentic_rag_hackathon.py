"""
Hackathon-optimized: Minimal Agentic RAG implementation
Focus: Working demo in hours, not days
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ============================================================================
# 1. MEMORY SYSTEM (Simple + Fast)
# ============================================================================

class QuickMemory:
    """Ultra-lightweight memory for hackathon."""
    
    def __init__(self):
        self.history = []  # Last 10 queries
        self.insights = {}  # topic -> list of insights
        self.cache = {}    # Simple cache
    
    def remember_query(self, query: str, result: Any, agent: str):
        """Remember a query and result."""
        self.history.append({
            "query": query,
            "result": result,
            "agent": agent,
            "time": datetime.now().isoformat()
        })
        # Keep only last 10
        if len(self.history) > 10:
            self.history.pop(0)
    
    def store_insight(self, topic: str, insight: str):
        """Store insight by topic."""
        if topic not in self.insights:
            self.insights[topic] = []
        self.insights[topic].append(insight)
    
    def recall_similar(self, topic: str) -> List[str]:
        """Recall similar insights."""
        return self.insights.get(topic, [])
    
    def get_context(self) -> str:
        """Get conversation context."""
        if not self.history:
            return "No prior context."
        
        recent = self.history[-3:]
        return "\n".join([
            f"Q: {h['query']}\nAgent: {h['agent']}"
            for h in recent
        ])


# ============================================================================
# 2. SIMPLE TOOLS (No complexity)
# ============================================================================

class ToolKit:
    """Ultra-simple tool registry."""
    
    def __init__(self):
        self.tools = {}
    
    def add_tool(self, name: str, func):
        """Add a tool function."""
        self.tools[name] = func
    
    def call(self, tool_name: str, **kwargs):
        """Call a tool."""
        if tool_name not in self.tools:
            return {"error": f"Tool {tool_name} not found"}
        try:
            return {"result": self.tools[tool_name](**kwargs)}
        except Exception as e:
            return {"error": str(e)}


# ============================================================================
# 3. REACT PLANNER (Minimal version)
# ============================================================================

class QuickReACT:
    """Minimal ReACT - Just thoughts + actions."""
    
    def __init__(self, memory: QuickMemory, tools: ToolKit):
        self.memory = memory
        self.tools = tools
        self.reasoning = []
    
    def think_and_act(self, query: str, agent_name: str) -> Dict[str, Any]:
        """Simple think-act-observe cycle."""
        
        self.reasoning = []
        
        # THOUGHT
        self.reasoning.append(f"💭 THOUGHT: Analyzing '{query}'")
        
        # Check memory
        context = self.memory.get_context()
        if context != "No prior context.":
            self.reasoning.append(f"📚 Found context: {context[:100]}...")
        
        # ACTION - call a tool
        self.reasoning.append(f"🔧 ACTION: Using {agent_name}")
        
        # OBSERVATION
        self.reasoning.append(f"👁️  OBSERVATION: Completed")
        
        return {
            "thoughts": self.reasoning,
            "context": context
        }


# ============================================================================
# 4. VECTOR SEARCH (Super simple)
# ============================================================================

def simple_similarity(s1: str, s2: str) -> float:
    """Simple text similarity (word overlap)."""
    words1 = set(s1.lower().split())
    words2 = set(s2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    overlap = len(words1 & words2)
    total = len(words1 | words2)
    return overlap / total if total > 0 else 0.0


class QuickVectorStore:
    """Minimal vector search (no ML, just string similarity)."""
    
    def __init__(self):
        self.items = {}  # id -> content
    
    def add(self, id: str, content: str):
        """Add content."""
        self.items[id] = content
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search by similarity."""
        scores = [
            (id, content, simple_similarity(query, content))
            for id, content in self.items.items()
        ]
        
        scores.sort(key=lambda x: x[2], reverse=True)
        
        return [
            {"id": id, "content": content, "score": score}
            for id, content, score in scores[:k]
            if score > 0.1  # Filter out too-low scores
        ]


# ============================================================================
# 5. INTEGRATION: Enhanced Agent Base
# ============================================================================

class AgenticAgent:
    """Agent with memory + tools + reasoning."""
    
    def __init__(self, name: str, memory: QuickMemory, tools: ToolKit):
        self.name = name
        self.memory = memory
        self.tools = tools
        self.react = QuickReACT(memory, tools)
    
    def execute_with_context(self, query: str, **kwargs):
        """Execute with memory + reasoning."""
        
        # Get augmented context
        thoughts = self.react.think_and_act(query, self.name)
        
        # Execute main logic (from original agent)
        result = self.run(query=query, **kwargs)
        
        # Remember it
        self.memory.remember_query(query, result, self.name)
        
        # Extract insights
        if "insights" in result:
            for insight in result.get("insights", [])[:3]:
                self.memory.store_insight("general", str(insight))
        
        # Return augmented result
        return {
            **result,
            "_reasoning_trace": thoughts["thoughts"],
            "_conversation_context": thoughts["context"]
        }
    
    def run(self, **kwargs):
        """Override this in subclasses."""
        raise NotImplementedError


# ============================================================================
# 6. EXPORT FOR USE IN YOUR AGENTS
# ============================================================================

def create_agentic_context():
    """Create all agentic RAG components in one call."""
    memory = QuickMemory()
    tools = ToolKit()
    vector_store = QuickVectorStore()
    
    # Add default tools
    tools.add_tool("recall_insights", lambda topic: memory.recall_similar(topic))
    tools.add_tool("search_vector", lambda query: vector_store.search(query))
    
    return {
        "memory": memory,
        "tools": tools,
        "vector_store": vector_store,
        "react": QuickReACT(memory, tools)
    }


__all__ = [
    "QuickMemory",
    "ToolKit",
    "QuickReACT",
    "QuickVectorStore",
    "AgenticAgent",
    "create_agentic_context",
    "simple_similarity"
]
