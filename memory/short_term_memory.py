"""
Short-term memory: conversation history and context.
"""

import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Optional, Any, Dict
from config import LOGS_DIR

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "memory.log"))
logger.setLevel(logging.INFO)


@dataclass
class ConversationTurn:
    """Single turn in agent conversation."""
    
    user_id: str
    session_id: str
    turn_number: int
    user_query: str
    agent_name: str
    agent_output: Dict[str, Any]
    duration_seconds: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dict."""
        d = asdict(self)
        d['timestamp'] = self.timestamp.isoformat()
        return d


class ShortTermMemory:
    """
    In-memory conversation history.
    Stores recent queries and responses for context continuity.
    """
    
    def __init__(self, max_turns: int = 50):
        """
        Initialize short-term memory.
        
        Args:
            max_turns: Maximum number of turns to keep in memory
        """
        self.turns: List[ConversationTurn] = []
        self.max_turns = max_turns
        self.session_turns: Dict[str, List[ConversationTurn]] = {}
        logger.info(f"Initialized ShortTermMemory (max_turns={max_turns})")
    
    def add_turn(self, turn: ConversationTurn) -> None:
        """
        Add a turn to conversation history.
        
        Args:
            turn: ConversationTurn to add
        """
        # Add to global history
        if len(self.turns) >= self.max_turns:
            removed = self.turns.pop(0)
            logger.debug(f"Removed oldest turn: {removed.user_query[:50]}...")
        
        self.turns.append(turn)
        
        # Add to session-specific history
        if turn.session_id not in self.session_turns:
            self.session_turns[turn.session_id] = []
        
        if len(self.session_turns[turn.session_id]) >= self.max_turns:
            self.session_turns[turn.session_id].pop(0)
        
        self.session_turns[turn.session_id].append(turn)
        
        logger.info(
            f"Added turn {turn.turn_number} for user {turn.user_id}: "
            f"{turn.user_query[:50]}... (agent: {turn.agent_name})"
        )
    
    def get_recent(self, k: int = 5, session_id: Optional[str] = None) -> List[ConversationTurn]:
        """
        Get last k turns.
        
        Args:
            k: Number of recent turns
            session_id: If provided, get turns from specific session
        
        Returns:
            List of recent turns
        """
        if session_id and session_id in self.session_turns:
            return self.session_turns[session_id][-k:]
        return self.turns[-k:]
    
    def get_context(self, k: int = 3, session_id: Optional[str] = None) -> str:
        """
        Get conversation context as formatted string for LLM.
        
        Args:
            k: Number of recent turns to include
            session_id: If provided, get turns from specific session
        
        Returns:
            Formatted context string
        """
        recent = self.get_recent(k=k, session_id=session_id)
        
        if not recent:
            return "No prior conversation history."
        
        context_lines = ["Recent Conversation History:"]
        for i, turn in enumerate(recent, 1):
            context_lines.append(
                f"{i}. Query: {turn.user_query}\n"
                f"   Agent: {turn.agent_name}\n"
                f"   Time: {turn.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        
        return "\n".join(context_lines)
    
    def search_by_agent(self, agent_name: str, k: int = 5) -> List[ConversationTurn]:
        """
        Get recent turns by specific agent.
        
        Args:
            agent_name: Name of agent to search for
            k: Number of results
        
        Returns:
            List of turns from that agent
        """
        matching = [t for t in self.turns if t.agent_name == agent_name]
        return matching[-k:]
    
    def search_by_query_substring(self, substring: str, k: int = 5) -> List[ConversationTurn]:
        """
        Search conversation history by query substring.
        
        Args:
            substring: Substring to search for (case-insensitive)
            k: Number of results
        
        Returns:
            List of matching turns
        """
        matching = [
            t for t in self.turns
            if substring.lower() in t.user_query.lower()
        ]
        return matching[-k:]
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get summary of a session.
        
        Args:
            session_id: Session ID to summarize
        
        Returns:
            Summary dict
        """
        if session_id not in self.session_turns:
            return {"session_id": session_id, "turns": 0, "summary": "No turns"}
        
        turns = self.session_turns[session_id]
        agents = set(t.agent_name for t in turns)
        total_duration = sum(t.duration_seconds for t in turns)
        
        return {
            "session_id": session_id,
            "turns": len(turns),
            "agents_used": list(agents),
            "total_duration_seconds": round(total_duration, 2),
            "first_turn": turns[0].timestamp.isoformat() if turns else None,
            "last_turn": turns[-1].timestamp.isoformat() if turns else None,
        }
    
    def clear_session(self, session_id: str) -> None:
        """Clear a specific session's memory."""
        if session_id in self.session_turns:
            del self.session_turns[session_id]
            logger.info(f"Cleared session {session_id}")
    
    def clear_all(self) -> None:
        """Clear all memory."""
        self.turns.clear()
        self.session_turns.clear()
        logger.info("Cleared all short-term memory")
