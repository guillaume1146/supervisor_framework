"""
State-related type definitions for the workflow system.
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class SupervisorOutPydantic(BaseModel):
    """Pydantic model for supervisor output - used for structured LLM output"""
    next_phase: str = Field(description="The next workflow phase to execute")
    intent: str = Field(description="Brief summary of what the user wants to accomplish")
    confidence: float = Field(description="Confidence level between 0.0 and 1.0", ge=0.0, le=1.0)


class SupervisorOut(TypedDict):
    """TypedDict for supervisor output - used in state management"""
    next_phase: str
    intent: str
    confidence: float


class WorkflowState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    params: Dict[str, Dict[str, Any]]
    results: Dict[str, Dict[str, Any]]
    supervisor_out: Optional[SupervisorOut]
    current_phase: Optional[str]
    awaiting_input: bool
    status: str
    error_count: int
    iteration_count: int
    error_message: Optional[str]