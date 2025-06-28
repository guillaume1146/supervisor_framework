"""
FastAPI chatbot endpoint implementation with updated imports.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Updated imports using new modular structure
from workflow_system import EnhancedParameterWorkflow, WorkflowConfig, WorkflowStatus
from workflow_system.workflows import PHASE_DEFINITIONS  # Auto-loaded from registry
from .models import ChatRequest, ChatResponse, ChatStatus, SessionInfo, SessionListResponse

logger = logging.getLogger(__name__)


class ChatbotService:
    """Service class to manage chatbot sessions and workflow integration"""
    
    def __init__(self):
        """Initialize the chatbot service"""
        # Configure workflow system
        self.workflow_config = WorkflowConfig(
            debug_mode=True,
            enable_auto_continuation=True,
            max_iterations=5
        )
        
        # Initialize workflow system with new modular PHASE_DEFINITIONS
        self.workflow = EnhancedParameterWorkflow(PHASE_DEFINITIONS, self.workflow_config)
        
        # In-memory session storage (use Redis/DB in production)
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"Chatbot service initialized with {len(PHASE_DEFINITIONS)} phases")
        logger.info(f"Available phases: {[p.name for p in PHASE_DEFINITIONS]}")
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return str(uuid.uuid4())
    
    def _get_chat_status(self, workflow_status: str, awaiting_input: bool) -> ChatStatus:
        """Convert workflow status to chat status"""
        if workflow_status == WorkflowStatus.COMPLETED.value:
            return ChatStatus.COMPLETED
        elif workflow_status == WorkflowStatus.FAILED.value:
            return ChatStatus.FAILED
        elif awaiting_input or workflow_status == WorkflowStatus.COLLECTING_PARAMS.value:
            return ChatStatus.WAITING_INPUT
        else:
            return ChatStatus.ACTIVE
    
    def _update_session_metadata(self, session_id: str, workflow_result: Dict[str, Any]):
        """Update session metadata with workflow information"""
        current_time = datetime.utcnow().isoformat()
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": current_time,
                "message_count": 0,
                "workflow_history": []
            }
        
        session = self.sessions[session_id]
        session["last_activity"] = current_time
        session["message_count"] += 1
        session["current_phase"] = workflow_result.get("current_phase")
        session["status"] = self._get_chat_status(
            workflow_result.get("status", ""), 
            workflow_result.get("awaiting_input", False)
        ).value
        session["collected_params"] = workflow_result.get("params", {})
        
        # Store latest workflow result
        session["latest_workflow_result"] = workflow_result
    
    def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process a chat message and return response"""
        try:
            session_id = request.session_id or self._generate_session_id()
            logger.info(f"Processing message for session {session_id}: '{request.message}'")
            if session_id not in self.sessions or request.session_id is None:
                logger.info(f"Starting new workflow for session {session_id}")
                result = self.workflow.run_workflow(request.message, session_id)
            else:
                logger.info(f"Continuing workflow for session {session_id}")
                result = self.workflow.add_user_input(request.message, session_id)
            
            self._update_session_metadata(session_id, result)
            
            response_message = "Hello! How can I help you today?"
            if result.get("messages"):
                last_message = result["messages"][-1]
                if hasattr(last_message, 'content'):
                    response_message = last_message.content
                else:
                    response_message = str(last_message)
            
            workflow_status = result.get("status", WorkflowStatus.PENDING.value)
            awaiting_input = result.get("awaiting_input", False)
            chat_status = self._get_chat_status(workflow_status, awaiting_input)
            workflow_results = None
            if chat_status == ChatStatus.COMPLETED:
                workflow_results = result.get("results", {})
                logger.info(f"🔧 CHATBOT - Status is COMPLETED, extracting results: {list(workflow_results.keys()) if workflow_results else 'None'}")
            else:
                logger.info(f"🔧 CHATBOT - Status is {chat_status}, not extracting results")
                logger.info(f"🔧 CHATBOT - Available results in state: {list(result.get('results', {}).keys())}")
            
            error_message = None
            if result.get("error"):
                error_message = result["error"]
                chat_status = ChatStatus.FAILED
            
            metadata = {
                "workflow_status": workflow_status,
                "current_phase": result.get("current_phase"),
                "iteration_count": result.get("iteration_count", 0),
                "error_count": result.get("error_count", 0)
            }
            
            response = ChatResponse(
                session_id=session_id,
                message=response_message,
                status=chat_status,
                awaiting_input=awaiting_input,
                workflow_results=workflow_results,
                error=error_message,
                metadata=metadata
            )
            
            logger.info(f"Response for session {session_id}: status={chat_status.value}, awaiting_input={awaiting_input}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            session_id = request.session_id or self._generate_session_id()
            
            return ChatResponse(
                session_id=session_id,
                message=f"I'm sorry, I encountered an error: {str(e)}",
                status=ChatStatus.FAILED,
                awaiting_input=False,
                error=str(e),
                metadata={"error_type": type(e).__name__}
            )
    
    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Get information about a specific session"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        return SessionInfo(
            session_id=session_id,
            status=ChatStatus(session.get("status", "active")),
            current_phase=session.get("current_phase"),
            collected_params=session.get("collected_params", {}),
            message_count=session.get("message_count", 0),
            created_at=session.get("created_at", ""),
            last_activity=session.get("last_activity", "")
        )
    
    def list_sessions(self) -> SessionListResponse:
        """List all active sessions"""
        session_infos = []
        
        for session_id in self.sessions:
            session_info = self.get_session_info(session_id)
            if session_info:
                session_infos.append(session_info)
        
        return SessionListResponse(
            sessions=session_infos,
            total_count=len(session_infos)
        )
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a specific session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False