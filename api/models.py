"""
FastAPI request/response models for the chatbot endpoint.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class ChatStatus(str, Enum):
    """Chat session status"""
    ACTIVE = "active"
    WAITING_INPUT = "waiting_input"
    COMPLETED = "completed"
    FAILED = "failed"


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User message", min_length=1)
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    session_id: str = Field(..., description="Session ID for this conversation")
    message: str = Field(..., description="Bot response message")
    status: ChatStatus = Field(..., description="Current session status")
    awaiting_input: bool = Field(False, description="Whether bot is waiting for user input")
    workflow_results: Optional[Dict[str, Any]] = Field(None, description="Workflow results if completed")
    error: Optional[str] = Field(None, description="Error message if any")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class FinancialDataSummary(BaseModel):
    """Summary of collected financial data"""
    phase: str
    completion_status: str
    collected_fields: Dict[str, str]
    data_quality_score: int
    ready_for_next_phase: bool
    
class SessionInfo(BaseModel):
    """Session information model"""
    session_id: str
    status: ChatStatus
    current_phase: Optional[str]
    collected_params: Dict[str, Any]
    message_count: int
    created_at: str
    last_activity: str


class SessionListResponse(BaseModel):
    """Response model for listing sessions"""
    sessions: List[SessionInfo]
    total_count: int