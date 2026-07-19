"""
Vector store and semantic search for content retrieval.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
from config import LOGS_DIR

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "retrieval.log"))
logger.setLevel(logging.INFO)


@dataclass
class Vector:
    """Vector representation with metadata."""
    
    id: str
    content: str
    vector: np.ndarray
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class SimpleEmbedder:
    """
    Simple embedder using character n-gram frequencies.
    (Production use would use real embeddings: OpenAI, SentenceTransformers, etc.)
    """
    
    def __init__(self, n: int = 3):
        """
        Initialize embedder.
        
        Args:
            n: N-gram size
        """
        self.n = n
        self.vocab = {}
        self.vocab_size = 1000  # Fixed embedding dimension
    
    def _get_ngrams(self, text: str) -> List[str]:
        """Get n-grams from text."""
        text = text.lower()
        return [text[i:i+self.n] for i in range(len(text) - self.n + 1)]
    
    def embed(self, text: str) -> np.ndarray:
        """
        Embed text to vector.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        ngrams = self._get_ngrams(text)
        
        # Count frequencies
        freq = {}
        for ngram in ngrams:
            freq[ngram] = freq.get(ngram, 0) + 1
        
        # Create vector based on frequencies (hashed)
        vector = np.zeros(self.vocab_size)
        for ngram, count in freq.items():
            idx = hash(ngram) % self.vocab_size
            vector[idx] += count
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Compute cosine similarity between vectors.
        
        Args:
            v1: Vector 1
            v2: Vector 2
        
        Returns:
            Similarity score 0-1
        """
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)


class VectorStore:
    """
    Local vector store for semantic search.
    Stores vectors in memory with optional persistence.
    """
    
    def __init__(self, embedder: Optional[SimpleEmbedder] = None):
        """
        Initialize vector store.
        
        Args:
            embedder: Optional embedder (uses SimpleEmbedder by default)
        """
        self.embedder = embedder or SimpleEmbedder()
        self.vectors: Dict[str, Vector] = {}
        logger.info("Initialized VectorStore")
    
    def add(
        self,
        id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add item to vector store.
        
        Args:
            id: Unique ID
            content: Content to embed and store
            metadata: Optional metadata
        """
        # Check if already exists
        if id in self.vectors:
            logger.warning(f"Vector {id} already exists, updating")
        
        # Embed content
        embedding = self.embedder.embed(content)
        
        # Create vector
        vector = Vector(
            id=id,
            content=content,
            vector=embedding,
            metadata=metadata or {}
        )
        
        self.vectors[id] = vector
        logger.debug(f"Added vector: {id}")
    
    def search(
        self,
        query: str,
        k: int = 5,
        min_similarity: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for similar items.
        
        Args:
            query: Search query
            k: Number of results
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of results with similarity scores
        """
        # Embed query
        query_vector = self.embedder.embed(query)
        
        # Compute similarities
        results = []
        for vector in self.vectors.values():
            similarity = self.embedder.similarity(query_vector, vector.vector)
            
            if similarity >= min_similarity:
                results.append({
                    "id": vector.id,
                    "content": vector.content,
                    "similarity": float(similarity),
                    "metadata": vector.metadata,
                    "created_at": vector.created_at.isoformat()
                })
        
        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        logger.debug(f"Search for '{query[:50]}...' found {len(results)} results")
        return results[:k]
    
    def remove(self, id: str) -> bool:
        """Remove item from store."""
        if id in self.vectors:
            del self.vectors[id]
            logger.debug(f"Removed vector: {id}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all vectors."""
        self.vectors.clear()
        logger.info("Cleared all vectors")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        total_size = sum(
            len(v.content) for v in self.vectors.values()
        )
        
        return {
            "total_items": len(self.vectors),
            "total_content_size_bytes": total_size,
            "avg_item_size_bytes": total_size // len(self.vectors) if self.vectors else 0,
            "embedding_dimension": 1000  # Fixed for SimpleEmbedder
        }


class RAGRetriever:
    """
    Retrieval-Augmented Generation retriever.
    Combines vector search with filtering.
    """
    
    def __init__(self, vector_store: VectorStore):
        """
        Initialize retriever.
        
        Args:
            vector_store: Vector store to search
        """
        self.store = vector_store
        logger.info("Initialized RAGRetriever")
    
    def retrieve(
        self,
        query: str,
        k: int = 5,
        min_similarity: float = 0.3,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve with optional filtering.
        
        Args:
            query: Search query
            k: Number of results
            min_similarity: Minimum similarity
            filters: Optional metadata filters
        
        Returns:
            List of results
        """
        # Search
        results = self.store.search(query, k=k*2, min_similarity=min_similarity)
        
        # Apply filters if provided
        if filters:
            filtered = []
            for result in results:
                if self._matches_filters(result, filters):
                    filtered.append(result)
            results = filtered
        
        # Return top k
        return results[:k]
    
    @staticmethod
    def _matches_filters(item: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if item matches all filters."""
        for key, value in filters.items():
            if item.get("metadata", {}).get(key) != value:
                return False
        return True
    
    def add_content(
        self,
        contents: List[tuple],  # List of (id, content, metadata) tuples
    ) -> None:
        """
        Add multiple contents to retriever.
        
        Args:
            contents: List of (id, content, metadata) tuples
        """
        for id_val, content, metadata in contents:
            self.store.add(id_val, content, metadata)
        
        logger.info(f"Added {len(contents)} items to retriever")


class ContentAugmenter:
    """Augment agent context with retrieved content."""
    
    def __init__(self, retriever: RAGRetriever):
        """Initialize augmenter."""
        self.retriever = retriever
    
    def augment(
        self,
        base_context: str,
        query: str,
        k: int = 3
    ) -> Dict[str, Any]:
        """
        Augment context with retrieved content.
        
        Args:
            base_context: Base context
            query: Query for retrieval
            k: Number of items to retrieve
        
        Returns:
            Augmented context dict
        """
        # Retrieve similar content
        retrieved = self.retriever.retrieve(query=query, k=k)
        
        # Format retrieved content
        retrieved_text = "\n".join([
            f"- [{r['id']}] {r['content'][:200]}... (similarity: {r['similarity']:.2f})"
            for r in retrieved
        ]) if retrieved else "No relevant content found."
        
        return {
            "base_context": base_context,
            "retrieved_count": len(retrieved),
            "retrieved_content": retrieved_text,
            "retrieved_items": retrieved,
            "augmented_context": f"{base_context}\n\nSimilar past insights:\n{retrieved_text}"
        }
