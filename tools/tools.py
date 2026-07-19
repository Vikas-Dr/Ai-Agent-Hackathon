"""
Built-in tools for agent use.
"""

import logging
from typing import Any, Optional
from tools.base_tool import Tool, ToolResult, Parameter, ToolRegistry
from config import LOGS_DIR

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "tools.log"))
logger.setLevel(logging.INFO)


class CacheLookupTool(Tool):
    """Look up cached results from memory."""
    
    name = "cache_lookup"
    description = "Look up cached analysis results from memory"
    parameters = [
        Parameter(name="cache_key", type_="string", required=True,
                 description="Key to look up in cache"),
        Parameter(name="default", type_="any", required=False,
                 description="Default value if cache miss")
    ]
    
    def __init__(self, memory_manager=None):
        """Initialize cache tool with optional memory manager."""
        self.memory_manager = memory_manager
    
    def execute(self, cache_key: str, default: Any = None, **kwargs) -> ToolResult:
        """Execute cache lookup."""
        try:
            if self.memory_manager is None:
                logger.debug(f"Cache tool not configured with memory manager")
                return ToolResult(success=False, error="Memory manager not configured")
            
            # Try to get from long-term memory
            cached = self.memory_manager.long_term.get_cached_insights(cache_key)
            
            if cached is not None:
                return ToolResult(
                    success=True,
                    data={"cache_hit": True, "insights": cached}
                )
            else:
                return ToolResult(
                    success=True,
                    data={"cache_hit": False, "insights": default}
                )
        
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class MemoryRetrievalTool(Tool):
    """Retrieve similar insights from memory."""
    
    name = "memory_retrieve"
    description = "Retrieve similar insights from long-term memory"
    parameters = [
        Parameter(name="query", type_="string", required=True,
                 description="Query to search memory with"),
        Parameter(name="k", type_="integer", required=False,
                 description="Number of results (default 5)"),
        Parameter(name="min_similarity", type_="float", required=False,
                 description="Minimum similarity threshold (0-1)")
    ]
    
    def __init__(self, memory_manager=None):
        """Initialize memory retrieval tool."""
        self.memory_manager = memory_manager
    
    def execute(self, query: str, k: int = 5, min_similarity: float = 0.3, **kwargs) -> ToolResult:
        """Execute memory retrieval."""
        try:
            if self.memory_manager is None:
                return ToolResult(success=False, error="Memory manager not configured")
            
            items = self.memory_manager.search_knowledge(
                query=query,
                k=k,
                search_type="similar"
            )
            
            retrieved = [
                {
                    "insight": item.insight,
                    "topic": item.topic,
                    "source_agent": item.source_agent,
                    "created_at": item.created_at.isoformat(),
                    "hit_count": item.hit_count
                }
                for item in items
            ]
            
            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "retrieved_count": len(retrieved),
                    "insights": retrieved
                }
            )
        
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class ConversationContextTool(Tool):
    """Get conversation context."""
    
    name = "get_context"
    description = "Get conversation context from memory"
    parameters = [
        Parameter(name="k", type_="integer", required=False,
                 description="Number of recent turns (default 5)"),
        Parameter(name="session_id", type_="string", required=False,
                 description="Session ID to get context from")
    ]
    
    def __init__(self, memory_manager=None):
        """Initialize context tool."""
        self.memory_manager = memory_manager
    
    def execute(self, k: int = 5, session_id: Optional[str] = None, **kwargs) -> ToolResult:
        """Execute context retrieval."""
        try:
            if self.memory_manager is None:
                return ToolResult(success=False, error="Memory manager not configured")
            
            context = self.memory_manager.get_augmented_context(
                user_query="",
                k=k,
                session_id=session_id
            )
            
            return ToolResult(success=True, data=context)
        
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class DataProcessingTool(Tool):
    """Basic data processing tool."""
    
    name = "process_data"
    description = "Process and aggregate data"
    parameters = [
        Parameter(name="operation", type_="string", required=True,
                 description="Operation: 'sum', 'avg', 'count'"),
        Parameter(name="data", type_="array", required=True,
                 description="Data to process")
    ]
    
    def execute(self, operation: str, data: list, **kwargs) -> ToolResult:
        """Execute data processing."""
        try:
            if operation == "sum":
                result = sum(data)
            elif operation == "avg":
                result = sum(data) / len(data) if data else 0
            elif operation == "count":
                result = len(data)
            else:
                return ToolResult(success=False, error=f"Unknown operation: {operation}")
            
            return ToolResult(
                success=True,
                data={"operation": operation, "result": result}
            )
        
        except Exception as e:
            return ToolResult(success=False, error=str(e))


def create_default_tools(memory_manager=None) -> ToolRegistry:
    """
    Create and return registry with default tools.
    
    Args:
        memory_manager: Optional MemoryManager instance
    
    Returns:
        ToolRegistry with default tools
    """
    registry = ToolRegistry()
    
    # Register built-in tools
    registry.register(CacheLookupTool(memory_manager))
    registry.register(MemoryRetrievalTool(memory_manager))
    registry.register(ConversationContextTool(memory_manager))
    registry.register(DataProcessingTool())
    
    logger.info("Created default tool registry with 4 tools")
    return registry
