"""
Main entry point for the Enhanced Parameter Collection Workflow System.
Updated for modular structure.
"""

import uvicorn
import logging
from dotenv import load_dotenv

# Updated imports for modular structure
from workflow_system import EnhancedParameterWorkflow, WorkflowConfig, WorkflowStatus
from workflow_system.workflows import PHASE_DEFINITIONS  # Auto-loads all phases
from test_cases import ChatbotTestCases

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def main():
    """Run the FastAPI application with modular structure"""
    print("🚀 Enhanced Parameter Collection Workflow System (Modular)")
    print("=" * 60)
    print()
    
    # Verify modular structure
    print("🔍 Verifying modular structure...")
    print(f"✅ Total phases loaded: {len(PHASE_DEFINITIONS)}")
    for phase in PHASE_DEFINITIONS:
        print(f"   📋 {phase.name}: {phase.description}")
    print()
    
    # Print test instructions
    ChatbotTestCases.print_postman_instructions()
    
    print("\n🎯 Starting FastAPI server with modular workflow system...")
    logger.info("Starting Enhanced Workflow Chatbot API with modular structure...")
    
    try:
        uvicorn.run(
            "api.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped gracefully")


if __name__ == "__main__":
    main()