"""
Tool interface and registry for extensible agent tools.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from config import LOGS_DIR

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "tools.log"))
logger.setLevel(logging.INFO)


@dataclass
class Parameter:
    """Tool parameter definition."""
    
    name: str
    type_: str
    required: bool = True
    description: str = ""
    default: Any = None


@dataclass
class ToolResult:
    """Result of tool execution."""
    
    success: bool
    data: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class Tool(ABC):
    """Abstract base class for all tools."""
    
    name: str
    description: str
    parameters: List[Parameter] = []
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool.
        
        Args:
            **kwargs: Tool-specific parameters
        
        Returns:
            ToolResult with execution outcome
        """
        pass
    
    def validate_params(self, **kwargs) -> bool:
        """
        Validate that required parameters are provided.
        
        Args:
            **kwargs: Parameters to validate
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                raise ValueError(f"Missing required parameter: {param.name}")
        return True
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for LLM."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type_,
                    "required": p.required,
                    "description": p.description
                }
                for p in self.parameters
            ]
        }


class ToolRegistry:
    """Registry for managing tools."""
    
    def __init__(self):
        """Initialize tool registry."""
        self.tools: Dict[str, Tool] = {}
        self.call_history: List[Dict[str, Any]] = []
        logger.info("Initialized ToolRegistry")
    
    def register(self, tool: Tool) -> None:
        """
        Register a new tool.
        
        Args:
            tool: Tool to register
        
        Raises:
            ValueError: If tool already registered
        """
        if tool.name in self.tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def unregister(self, tool_name: str) -> None:
        """Unregister a tool."""
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")
    
    def get(self, tool_name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of tool
        
        Returns:
            Tool or None if not found
        """
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools.
        
        Returns:
            List of tool schemas
        """
        return [tool.get_schema() for tool in self.tools.values()]
    
    def call(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Call a tool.
        
        Args:
            tool_name: Name of tool to call
            **kwargs: Tool parameters
        
        Returns:
            ToolResult
        
        Raises:
            ValueError: If tool not found
        """
        import time
        
        tool = self.get(tool_name)
        if not tool:
            error_msg = f"Unknown tool: {tool_name}"
            logger.error(error_msg)
            return ToolResult(success=False, error=error_msg)
        
        try:
            # Validate parameters
            tool.validate_params(**kwargs)
            
            # Execute tool
            start_time = time.time()
            result = tool.execute(**kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            # Update result
            result.duration_ms = duration_ms
            
            # Log call
            self.call_history.append({
                "tool": tool_name,
                "params": kwargs,
                "success": result.success,
                "duration_ms": duration_ms,
                "timestamp": datetime.now().isoformat()
            })
            
            if result.success:
                logger.info(f"Tool call succeeded: {tool_name} ({duration_ms:.1f}ms)")
            else:
                logger.warning(f"Tool call failed: {tool_name} - {result.error}")
            
            return result
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Tool execution error: {tool_name} - {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)
    
    def __getitem__(self, name: str) -> Tool:
        """Enable dict-like access."""
        tool = self.get(name)
        if not tool:
            raise KeyError(f"Tool not found: {name}")
        return tool
    
    def __contains__(self, name: str) -> bool:
        """Check if tool is registered."""
        return name in self.tools
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_calls = len(self.call_history)
        successful = sum(1 for c in self.call_history if c['success'])
        failed = total_calls - successful
        avg_duration = (
            sum(c['duration_ms'] for c in self.call_history) / total_calls
            if total_calls > 0 else 0
        )
        
        return {
            "total_tools": len(self.tools),
            "total_calls": total_calls,
            "successful_calls": successful,
            "failed_calls": failed,
            "avg_duration_ms": round(avg_duration, 2)
        }
