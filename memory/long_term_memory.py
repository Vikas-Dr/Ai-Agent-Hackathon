"""
Long-term memory: knowledge base with semantic search.
"""

import json
import logging
import sqlite3
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Any, Dict
import numpy as np
from config import LOGS_DIR, ASSETS_DIR

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "memory.log"))
logger.setLevel(logging.INFO)


@dataclass
class KnowledgeItem:
    """Single knowledge item in long-term memory."""
    
    id: str
    topic: str
    insight: str
    source_agent: str
    created_at: datetime
    hit_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dict."""
        d = asdict(self)
        d['created_at'] = self.created_at.isoformat()
        return d


class LongTermMemory:
    """
    Persistent knowledge base for storing insights and learnings.
    Uses SQLite for storage, implements string similarity search.
    (Vector embeddings can be added later with Chroma/Pinecone)
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize long-term memory.
        
        Args:
            db_path: Path to SQLite database (default: assets/knowledge_base.db)
        """
        if db_path is None:
            db_path = str(ASSETS_DIR / "knowledge_base.db")
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        self._init_db()
        logger.info(f"Initialized LongTermMemory at {self.db_path}")
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        cursor = self.conn.cursor()
        
        # Create knowledge table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                insight TEXT NOT NULL,
                source_agent TEXT NOT NULL,
                created_at TEXT NOT NULL,
                hit_count INTEGER DEFAULT 0,
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        # Create insights cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insight_cache (
                cache_key TEXT PRIMARY KEY,
                insights TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
        """)
        
        # Create indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_topic ON knowledge(topic)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent ON knowledge(source_agent)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created ON knowledge(created_at)")
        
        self.conn.commit()
        logger.debug("Database schema initialized")
    
    def store_insight(
        self,
        topic: str,
        insight: str,
        source_agent: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a new insight in long-term memory.
        
        Args:
            topic: Topic/category of insight
            insight: Insight text
            source_agent: Agent that generated this
            metadata: Optional metadata dict
        
        Returns:
            ID of stored item
        """
        item_id = f"{source_agent}_{topic}_{int(datetime.now().timestamp())}"
        
        item = KnowledgeItem(
            id=item_id,
            topic=topic,
            insight=insight,
            source_agent=source_agent,
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO knowledge 
            (id, topic, insight, source_agent, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            item.id,
            item.topic,
            item.insight,
            item.source_agent,
            item.created_at.isoformat(),
            json.dumps(item.metadata)
        ))
        
        self.conn.commit()
        logger.info(f"Stored insight: {item_id} (topic: {topic}, agent: {source_agent})")
        
        return item_id
    
    def search_by_topic(self, topic: str, k: int = 5) -> List[KnowledgeItem]:
        """
        Search insights by topic.
        
        Args:
            topic: Topic to search for
            k: Number of results
        
        Returns:
            List of knowledge items
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM knowledge
            WHERE topic LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (f"%{topic}%", k))
        
        rows = cursor.fetchall()
        items = []
        
        for row in rows:
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
            item = KnowledgeItem(
                id=row['id'],
                topic=row['topic'],
                insight=row['insight'],
                source_agent=row['source_agent'],
                created_at=datetime.fromisoformat(row['created_at']),
                hit_count=row['hit_count'],
                metadata=metadata
            )
            items.append(item)
            
            # Increment hit count
            cursor.execute(
                "UPDATE knowledge SET hit_count = hit_count + 1 WHERE id = ?",
                (row['id'],)
            )
        
        self.conn.commit()
        logger.debug(f"Found {len(items)} items for topic: {topic}")
        
        return items
    
    def search_by_agent(self, agent_name: str, k: int = 5) -> List[KnowledgeItem]:
        """
        Search insights by source agent.
        
        Args:
            agent_name: Agent name to search for
            k: Number of results
        
        Returns:
            List of knowledge items
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM knowledge
            WHERE source_agent = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (agent_name, k))
        
        rows = cursor.fetchall()
        items = []
        
        for row in rows:
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
            item = KnowledgeItem(
                id=row['id'],
                topic=row['topic'],
                insight=row['insight'],
                source_agent=row['source_agent'],
                created_at=datetime.fromisoformat(row['created_at']),
                hit_count=row['hit_count'],
                metadata=metadata
            )
            items.append(item)
        
        logger.debug(f"Found {len(items)} items from agent: {agent_name}")
        return items
    
    def string_similarity(self, s1: str, s2: str) -> float:
        """
        Simple string similarity using character overlap.
        
        Args:
            s1: First string
            s2: Second string
        
        Returns:
            Similarity score 0-1
        """
        s1_lower = s1.lower()
        s2_lower = s2.lower()
        
        # Check for substring match
        if s1_lower in s2_lower or s2_lower in s1_lower:
            return 0.8
        
        # Word overlap
        words1 = set(s1_lower.split())
        words2 = set(s2_lower.split())
        
        if not words1 or not words2:
            return 0.0
        
        overlap = len(words1 & words2)
        total = len(words1 | words2)
        
        return overlap / total if total > 0 else 0.0
    
    def search_similar(self, query: str, k: int = 5, min_similarity: float = 0.3) -> List[KnowledgeItem]:
        """
        Search for similar insights using string similarity.
        
        Args:
            query: Query string
            k: Number of results
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of similar knowledge items
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM knowledge ORDER BY hit_count DESC, created_at DESC")
        rows = cursor.fetchall()
        
        scored_items = []
        
        for row in rows:
            # Compute similarity
            topic_sim = self.string_similarity(query, row['topic'])
            insight_sim = self.string_similarity(query, row['insight'][:200])  # Use first 200 chars
            
            avg_sim = (topic_sim * 0.3 + insight_sim * 0.7)  # Weight insight more
            
            if avg_sim >= min_similarity:
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                item = KnowledgeItem(
                    id=row['id'],
                    topic=row['topic'],
                    insight=row['insight'],
                    source_agent=row['source_agent'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    hit_count=row['hit_count'],
                    metadata=metadata
                )
                scored_items.append((item, avg_sim))
        
        # Sort by similarity and return top k
        scored_items.sort(key=lambda x: x[1], reverse=True)
        items = [item for item, _ in scored_items[:k]]
        
        logger.debug(f"Found {len(items)} similar items for query: {query[:50]}...")
        return items
    
    def cache_insights(
        self,
        cache_key: str,
        insights: List[str],
        ttl_seconds: int = 3600
    ) -> None:
        """
        Cache insights for quick retrieval.
        
        Args:
            cache_key: Key to store under
            insights: List of insights to cache
            ttl_seconds: Time-to-live in seconds (default 1 hour)
        """
        from datetime import timedelta
        
        now = datetime.now()
        expires_at = now + timedelta(seconds=ttl_seconds)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO insight_cache
            (cache_key, insights, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        """, (
            cache_key,
            json.dumps(insights),
            now.isoformat(),
            expires_at.isoformat()
        ))
        
        self.conn.commit()
        logger.debug(f"Cached insights under key: {cache_key}")
    
    def get_cached_insights(self, cache_key: str) -> Optional[List[str]]:
        """
        Retrieve cached insights if not expired.
        
        Args:
            cache_key: Key to retrieve
        
        Returns:
            List of insights or None if expired/not found
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT insights, expires_at FROM insight_cache
            WHERE cache_key = ?
        """, (cache_key,))
        
        row = cursor.fetchone()
        
        if not row:
            return None
        
        expires_at = datetime.fromisoformat(row['expires_at'])
        
        if datetime.now() > expires_at:
            # Cache expired, delete it
            cursor.execute("DELETE FROM insight_cache WHERE cache_key = ?", (cache_key,))
            self.conn.commit()
            logger.debug(f"Cache expired for key: {cache_key}")
            return None
        
        insights = json.loads(row['insights'])
        logger.debug(f"Retrieved cached insights for key: {cache_key}")
        return insights
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about knowledge base.
        
        Returns:
            Stats dict
        """
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM knowledge")
        total_items = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(DISTINCT topic) as count FROM knowledge")
        total_topics = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(DISTINCT source_agent) as count FROM knowledge")
        total_agents = cursor.fetchone()['count']
        
        cursor.execute("SELECT SUM(hit_count) as total FROM knowledge")
        total_hits = cursor.fetchone()['total'] or 0
        
        return {
            "total_items": total_items,
            "total_topics": total_topics,
            "total_agents": total_agents,
            "total_hits": total_hits,
            "database_path": str(self.db_path)
        }
    
    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
        logger.info("Closed long-term memory database")
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.close()
        except:
            pass
