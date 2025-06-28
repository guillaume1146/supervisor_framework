"""
FastAPI application setup and endpoints with updated imports.
"""

import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .chatbot import ChatbotService
from .models import ChatRequest, ChatResponse, SessionInfo, SessionListResponse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced Workflow Chatbot API (Modular v2.0)",
    description="A chatbot API with intelligent parameter collection using modular LangGraph workflows",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot service
chatbot_service = ChatbotService()


def get_chatbot_service() -> ChatbotService:
    """Dependency to get chatbot service instance"""
    return chatbot_service


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    service: ChatbotService = Depends(get_chatbot_service)
) -> ChatResponse:
    """
    Main chat endpoint for processing user messages.
    
    Supports the new modular workflow structure with auto-registered phases.
    """
    try:
        response = service.process_message(request)
        return response
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/phases")
async def list_phases():
    """List all available workflow phases"""
    from workflow_system.workflows import get_workflow_registry
    
    registry = get_workflow_registry()
    phases = []
    
    for phase in registry.get_all_phases():
        phases.append({
            "name": phase.name,
            "description": phase.description,
            "timeout_seconds": phase.timeout_seconds
        })
    
    return {
        "phases": phases,
        "total_count": len(phases),
        "version": "2.0.0 - Modular Structure"
    }


@app.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    service: ChatbotService = Depends(get_chatbot_service)
) -> SessionListResponse:
    """List all active chat sessions"""
    return service.list_sessions()


@app.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session(
    session_id: str,
    service: ChatbotService = Depends(get_chatbot_service)
) -> SessionInfo:
    """Get information about a specific session"""
    session_info = service.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_info


@app.delete("/sessions/{session_id}")
async def clear_session(
    session_id: str,
    service: ChatbotService = Depends(get_chatbot_service)
) -> dict:
    """Clear a specific session"""
    success = service.clear_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": f"Session {session_id} cleared successfully"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from workflow_system.workflows import get_workflow_registry
    
    registry = get_workflow_registry()
    
    return {
        "status": "healthy", 
        "message": "Chatbot API is running",
        "version": "2.0.0 - Modular Structure",
        "phases_loaded": len(registry.get_all_phases()),
        "available_phases": registry.list_phase_names()
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Enhanced Workflow Chatbot API",
        "version": "2.0.0 - Modular Structure",
        "endpoints": {
            "chat": "/chat",
            "phases": "/phases",
            "sessions": "/sessions",
            "health": "/health",
            "docs": "/docs"
        }
    }