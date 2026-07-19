"""
Simple RAG (Retrieval-Augmented Generation) for DevPulse.
Stores insights and retrieves similar ones for context.
"""

import json
from typing import List, Dict

class SimpleRAG:
    """Simple in-memory RAG without vector databases."""
    
    def __init__(self):
        self.insights_db = []
        self.load_default_insights()
    
    def load_default_insights(self):
        """Load default DevRel insights."""
        self.insights_db = [
            {"topic": "API Design", "insight": "API Design tutorials drive 45% higher developer signups"},
            {"topic": "Tutorial", "insight": "Code examples with runnable snippets have 3x engagement"},
            {"topic": "Backend", "insight": "Backend developers show 2x conversion to API signups"},
            {"topic": "Security", "insight": "Authentication guides have highest search ranking"},
            {"topic": "Length", "insight": "Content under 1500 words has highest completion rate"},
            {"topic": "Timing", "insight": "Content after framework releases gets 60% more views"},
        ]
    
    def retrieve(self, query: str, limit: int = 3) -> List[Dict]:
        """Retrieve relevant insights for a query."""
        query_lower = query.lower()
        scored = []
        
        for item in self.insights_db:
            insight_lower = f"{item['topic']} {item['insight']}".lower()
            # Simple keyword matching
            matches = sum(1 for word in query_lower.split() if word in insight_lower)
            if matches > 0:
                scored.append((item, matches))
        
        # Return top matches
        scored.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in scored[:limit]]
    
    def add_insight(self, topic: str, insight: str):
        """Add new insight to database."""
        self.insights_db.append({"topic": topic, "insight": insight})
    
    def generate_with_context(self, prompt: str) -> str:
        """Generate response with RAG context."""
        retrieved = self.retrieve(prompt)
        context = "\n".join([f"- {item['insight']}" for item in retrieved])
        
        return f"""Based on similar content patterns:
{context}

Recommendation: {prompt}"""

# Global RAG instance
rag = SimpleRAG()

def get_rag_insights(query: str) -> List[Dict]:
    """Get insights from RAG."""
    return rag.retrieve(query)

def store_insight(topic: str, insight: str):
    """Store new insight."""
    rag.add_insight(topic, insight)

def generate_with_rag(prompt: str) -> str:
    """Generate with RAG context."""
    return rag.generate_with_context(prompt)
