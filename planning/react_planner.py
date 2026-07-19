"""
ReACT (Reasoning-Action-Observation-Thinking) planner for multi-step agent reasoning.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Dict, Optional, Callable
from config import LOGS_DIR

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "planning.log"))
logger.setLevel(logging.INFO)


@dataclass
class Thought:
    """Agent's reasoning step."""
    
    text: str
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Action:
    """Agent's planned action."""
    
    tool_name: str
    parameters: Dict[str, Any]
    description: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Observation:
    """Result of action execution."""
    
    result: Any
    summary: str
    success: bool
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ReACTStep:
    """Complete ReACT cycle: Thought → Action → Observation."""
    
    step_number: int
    thought: Thought
    action: Action
    observation: Observation
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ReACTPlan:
    """Complete ReACT plan with all steps."""
    
    steps: List[ReACTStep] = field(default_factory=list)
    final_answer: str = ""
    reasoning_trace: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def add_step(self, step: ReACTStep) -> None:
        """Add a step to the plan."""
        self.steps.append(step)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict."""
        return {
            "steps": len(self.steps),
            "final_answer": self.final_answer,
            "reasoning_trace_length": len(self.reasoning_trace),
            "reasoning_trace": self.reasoning_trace[:10],  # First 10 for brevity
            "timestamp": self.timestamp.isoformat()
        }


class ReACTPlanner:
    """
    ReACT planning engine for multi-step agent reasoning.
    
    Implements the Reasoning-Action-Observation-Thinking loop:
    1. THOUGHT: What should I do?
    2. ACTION: Select and execute tool
    3. OBSERVATION: Analyze result
    4. REFLECTION: Do I need more steps?
    5. (repeat or ANSWER)
    """
    
    def __init__(
        self,
        memory_manager: Optional[Any] = None,
        tools: Optional[Any] = None,
        llm_client: Optional[Any] = None,
        max_steps: int = 5
    ):
        """
        Initialize ReACT planner.
        
        Args:
            memory_manager: Optional memory manager
            tools: Optional tool registry
            llm_client: Optional LLM client for thought generation
            max_steps: Maximum planning steps
        """
        self.memory_manager = memory_manager
        self.tools = tools
        self.llm_client = llm_client
        self.max_steps = max_steps
        logger.info(f"Initialized ReACTPlanner (max_steps={max_steps})")
    
    def plan(self, query: str, context: Optional[Dict[str, Any]] = None) -> ReACTPlan:
        """
        Generate and execute a ReACT plan.
        
        Args:
            query: User query to plan for
            context: Optional context dict
        
        Returns:
            ReACTPlan with all steps
        """
        plan = ReACTPlan()
        context = context or {}
        
        plan.reasoning_trace.append(f"🎯 Planning for query: {query}")
        
        for step_num in range(self.max_steps):
            # STEP 1: THOUGHT
            thought = self._generate_thought(
                query=query,
                step_num=step_num,
                prior_steps=plan.steps,
                context=context
            )
            plan.reasoning_trace.append(f"💭 THOUGHT {step_num + 1}: {thought.text}")
            
            # Check if we should stop
            if "stop" in thought.text.lower() or "done" in thought.text.lower():
                plan.reasoning_trace.append(f"✋ Stopping: Already have sufficient answer")
                break
            
            # STEP 2: ACTION
            action = self._select_action(
                thought=thought,
                step_num=step_num,
                context=context
            )
            
            if action is None:
                plan.reasoning_trace.append(f"⚠️  No action selected, stopping")
                break
            
            plan.reasoning_trace.append(
                f"🔧 ACTION {step_num + 1}: {action.tool_name} - {action.description}"
            )
            
            # STEP 3: OBSERVATION
            observation = self._execute_action(action)
            plan.reasoning_trace.append(f"👁️  OBSERVATION {step_num + 1}: {observation.summary}")
            
            if not observation.success:
                plan.reasoning_trace.append(f"❌ Action failed: {observation.error}")
            
            # Create step
            step = ReACTStep(
                step_number=step_num + 1,
                thought=thought,
                action=action,
                observation=observation
            )
            plan.add_step(step)
            
            # STEP 4: REFLECTION
            should_stop = self._should_stop(observation, step_num, plan.steps)
            if should_stop:
                plan.reasoning_trace.append(f"🛑 Reflection: Have enough info, stopping")
                break
        
        # Final answer
        plan.final_answer = self._extract_final_answer(plan.steps)
        plan.reasoning_trace.append(f"✨ ANSWER: {plan.final_answer}")
        
        logger.info(f"Planning complete: {len(plan.steps)} steps executed")
        return plan
    
    def _generate_thought(
        self,
        query: str,
        step_num: int,
        prior_steps: List[ReACTStep],
        context: Dict[str, Any]
    ) -> Thought:
        """Generate reasoning thought."""
        
        if step_num == 0:
            # First step: analyze what we need
            text = (
                f"The user is asking: '{query}'\n"
                f"I need to: 1) Check memory for context, "
                f"2) Plan which tools to use, "
                f"3) Retrieve relevant information"
            )
        else:
            # Subsequent steps: reflect on progress
            last_obs = prior_steps[-1].observation
            text = (
                f"Last action result: {last_obs.summary}\n"
                f"Status: {'✓ Success' if last_obs.success else '✗ Failed'}\n"
                f"Next: I need to {"use another tool" if not last_obs.success else "synthesize results"}"
            )
        
        return Thought(
            text=text,
            reasoning=f"Step {step_num + 1}: Reasoning about next action"
        )
    
    def _select_action(
        self,
        thought: Thought,
        step_num: int,
        context: Dict[str, Any]
    ) -> Optional[Action]:
        """Select which action/tool to use."""
        
        # Simple heuristic-based selection for now
        # (Could use LLM for more intelligent selection)
        
        if step_num == 0:
            # First step: check memory
            return Action(
                tool_name="get_context",
                parameters={"k": 3},
                description="Retrieve conversation context from memory"
            )
        elif step_num == 1:
            # Second step: retrieve similar knowledge
            return Action(
                tool_name="memory_retrieve",
                parameters={"query": context.get("query", ""), "k": 5},
                description="Search memory for similar insights"
            )
        elif step_num == 2:
            # Third step: check cache
            return Action(
                tool_name="cache_lookup",
                parameters={"cache_key": f"analysis_{context.get('topic', 'general')}"},
                description="Check for cached analysis results"
            )
        
        # No more actions
        return None
    
    def _execute_action(self, action: Action) -> Observation:
        """Execute an action."""
        
        try:
            if self.tools is None:
                return Observation(
                    result=None,
                    summary="Tools not configured",
                    success=False,
                    error="Tool registry not available"
                )
            
            # Call tool
            tool_result = self.tools.call(action.tool_name, **action.parameters)
            
            return Observation(
                result=tool_result.data,
                summary=f"Tool executed: {action.tool_name}",
                success=tool_result.success,
                error=tool_result.error
            )
        
        except Exception as e:
            return Observation(
                result=None,
                summary=f"Tool execution error: {str(e)[:100]}",
                success=False,
                error=str(e)
            )
    
    def _should_stop(
        self,
        observation: Observation,
        step_num: int,
        steps: List[ReACTStep]
    ) -> bool:
        """Decide if we should stop planning."""
        
        # Stop if failed
        if not observation.success:
            return True
        
        # Stop if max steps reached
        if step_num >= self.max_steps - 1:
            return True
        
        # Stop if we have enough data
        if observation.result and isinstance(observation.result, dict):
            if observation.result.get("cache_hit"):
                return True  # Found cached result
            if observation.result.get("retrieved_count", 0) > 3:
                return True  # Found enough similar items
        
        return False
    
    def _extract_final_answer(self, steps: List[ReACTStep]) -> str:
        """Extract final answer from all steps."""
        
        if not steps:
            return "No steps executed"
        
        # Summarize results from all steps
        summaries = [s.observation.summary for s in steps if s.observation.success]
        
        if not summaries:
            return "No successful actions"
        
        return f"Completed {len(summaries)} successful steps: " + ", ".join(summaries[:3])


class AdaptiveReACTPlanner(ReACTPlanner):
    """
    Enhanced ReACT planner with adaptation based on feedback.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize adaptive planner."""
        super().__init__(*args, **kwargs)
        self.plan_history: List[ReACTPlan] = []
    
    def plan_with_feedback(
        self,
        query: str,
        feedback_fn: Optional[Callable[[str], bool]] = None,
        max_iterations: int = 3
    ) -> ReACTPlan:
        """
        Execute plan with feedback-based adaptation.
        
        Args:
            query: Query to plan for
            feedback_fn: Optional function to evaluate plan (returns True if good)
            max_iterations: Max adaptation iterations
        
        Returns:
            Best plan found
        """
        best_plan = None
        
        for iteration in range(max_iterations):
            logger.info(f"Planning iteration {iteration + 1}/{max_iterations}")
            
            # Generate plan
            plan = self.plan(query)
            self.plan_history.append(plan)
            
            # Evaluate plan
            if feedback_fn is None or feedback_fn(plan.final_answer):
                logger.info("Plan accepted!")
                return plan
            
            # Adapt and retry
            best_plan = plan
            logger.info("Plan needs improvement, retrying...")
        
        logger.info("Returning best plan after max iterations")
        return best_plan or self.plan(query)
