"""
Unified memory manager combining short-term and long-term memory.
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from memory.short_term_memory import ShortTermMemory, ConversationTurn
from memory.long_term_memory import LongTermMemory, KnowledgeItem
from config import LOGS_DIR

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "memory.log"))
logger.setLevel(logging.INFO)


class MemoryManager:
    """
    Unified interface for short-term and long-term memory.
    Manages conversation context and knowledge base.
    """
    
    def __init__(self, ltm_db_path: Optional[str] = None):
        """
        Initialize memory manager.
        
        Args:
            ltm_db_path: Path to long-term memory database
        """
        self.short_term = ShortTermMemory(max_turns=50)
        self.long_term = LongTermMemory(db_path=ltm_db_path)
        logger.info("Initialized MemoryManager")
    
    def store_turn(
        self,
        user_id: str,
        session_id: str,
        turn_number: int,
        user_query: str,
        agent_name: str,
        agent_output: Dict[str, Any],
        duration_seconds: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Store a complete agent turn in memory.
        
        Args:
            user_id: User ID
            session_id: Session ID
            turn_number: Turn number in session
            user_query: User's query
            agent_name: Name of agent
            agent_output: Agent's output/result
            duration_seconds: Execution duration
            metadata: Additional metadata
        """
        turn = ConversationTurn(
            user_id=user_id,
            session_id=session_id,
            turn_number=turn_number,
            user_query=user_query,
            agent_name=agent_name,
            agent_output=agent_output,
            duration_seconds=duration_seconds,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        # Store in short-term memory
        self.short_term.add_turn(turn)
        
        # Extract and store insights in long-term memory
        self._extract_and_store_insights(turn)
    
    def _extract_and_store_insights(self, turn: ConversationTurn) -> None:
        """
        Extract insights from agent output and store in long-term memory.
        
        Args:
            turn: Conversation turn
        """
        agent_output = turn.agent_output
        
        # Extract insights based on agent type
        if turn.agent_name == "AnalyzerAgent":
            if "insights" in agent_output:
                topic = "analyzer_insights"
                for insight in agent_output.get("insights", [])[:3]:  # Store top 3
                    self.long_term.store_insight(
                        topic=topic,
                        insight=str(insight),
                        source_agent=turn.agent_name,
                        metadata={"query": turn.user_query[:100]}
                    )
        
        elif turn.agent_name == "StrategistAgent":
            topic = "strategy_gaps"
            gaps = agent_output.get("gaps", [])
            if gaps:
                gap_summary = ", ".join(gaps[:5])
                self.long_term.store_insight(
                    topic=topic,
                    insight=gap_summary,
                    source_agent=turn.agent_name,
                    metadata={"gap_count": len(gaps)}
                )
        
        elif turn.agent_name == "PredictorAgent":
            topic = "predictions"
            score = agent_output.get("predicted_score", 0)
            confidence = agent_output.get("confidence", "unknown")
            self.long_term.store_insight(
                topic=topic,
                insight=f"Score: {score}, Confidence: {confidence}",
                source_agent=turn.agent_name,
                metadata={"score": score, "confidence": confidence}
            )
    
    def get_conversation_context(
        self,
        k: int = 5,
        session_id: Optional[str] = None
    ) -> str:
        """
        Get formatted conversation context.
        
        Args:
            k: Number of recent turns
            session_id: Session to get context from
        
        Returns:
            Formatted context string
        """
        return self.short_term.get_context(k=k, session_id=session_id)
    
    def get_recent_turns(
        self,
        k: int = 5,
        session_id: Optional[str] = None
    ) -> List[ConversationTurn]:
        """
        Get recent turns from memory.
        
        Args:
            k: Number of recent turns
            session_id: Session to get turns from
        
        Returns:
            List of conversation turns
        """
        return self.short_term.get_recent(k=k, session_id=session_id)
    
    def search_knowledge(
        self,
        query: str,
        k: int = 5,
        search_type: str = "similar"
    ) -> List[KnowledgeItem]:
        """
        Search the knowledge base.
        
        Args:
            query: Search query
            k: Number of results
            search_type: "similar", "topic", or "agent"
        
        Returns:
            List of knowledge items
        """
        if search_type == "similar":
            return self.long_term.search_similar(query=query, k=k)
        elif search_type == "topic":
            return self.long_term.search_by_topic(topic=query, k=k)
        else:
            return self.long_term.search_by_agent(agent_name=query, k=k)
    
    def get_augmented_context(
        self,
        user_query: str,
        k: int = 3,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get augmented context combining conversation + knowledge base.
        
        Args:
            user_query: Current user query
            k: Number of items to retrieve
            session_id: Current session ID
        
        Returns:
            Dict with conversation context and retrieved knowledge
        """
        # Get recent conversation
        conversation = self.get_conversation_context(k=k, session_id=session_id)
        
        # Search knowledge base
        knowledge = self.search_knowledge(query=user_query, k=k)
        
        knowledge_summary = "\n".join([
            f"- {item.insight} (from {item.source_agent}, "
            f"created {item.created_at.strftime('%Y-%m-%d')})"
            for item in knowledge
        ]) if knowledge else "No relevant past insights found."
        
        return {
            "conversation_context": conversation,
            "retrieved_knowledge": knowledge_summary,
            "knowledge_items": [item.to_dict() for item in knowledge],
            "retrieval_timestamp": datetime.now().isoformat()
        }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about memory usage.
        
        Returns:
            Stats dict
        """
        sessions = len(self.short_term.session_turns)
        total_turns = len(self.short_term.turns)
        ltm_stats = self.long_term.get_stats()
        
        return {
            "short_term": {
                "sessions": sessions,
                "total_turns": total_turns,
                "max_capacity": self.short_term.max_turns
            },
            "long_term": ltm_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def export_memory(self, output_path: str) -> None:
        """
        Export memory state to JSON file.
        
        Args:
            output_path: Path to save JSON
        """
        import json
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "short_term_turns": [t.to_dict() for t in self.short_term.turns],
            "sessions": {
                sid: [t.to_dict() for t in turns]
                for sid, turns in self.short_term.session_turns.items()
            },
            "stats": self.get_memory_stats()
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported memory state to {output_path}")
    
    def clear_session(self, session_id: str) -> None:
        """Clear a session from memory."""
        self.short_term.clear_session(session_id)
        logger.info(f"Cleared session {session_id}")
    
    def close(self) -> None:
        """Close all memory connections."""
        self.long_term.close()
        logger.info("Closed MemoryManager")
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.close()
