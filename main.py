"""
Main entry point for the Enhanced Parameter Collection Workflow System.
"""

import logging


from workflow_system import EnhancedParameterWorkflow, WorkflowConfig, WorkflowStatus, PHASE_DEFINITIONS
from workflow_system.tests import run_enhanced_tests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Main demo function"""
    print("🚀 Enhanced Parameter Collection Workflow Demo")
    print("=" * 60)
    
    config = WorkflowConfig(debug_mode=True)
    workflow = EnhancedParameterWorkflow(PHASE_DEFINITIONS, config)
    
    # Demo 1: Complete workflow
    print("\n📝 Demo 1: Complete parameters")
    result = workflow.run_workflow("Generate a monthly report for Alice", "demo1")
    
    if result.get("status") == WorkflowStatus.COMPLETED.value:
        print("✅ Success! Workflow completed")
    else:
        print(f"⚠️ Status: {result.get('status')}")
    
    # Demo 2: Missing parameters
    print("\n📝 Demo 2: Missing parameters (parameter collection)")
    result = workflow.run_workflow("Generate a report", "demo2")
    
    if result.get("awaiting_input"):
        print("✅ Success! System requesting missing parameters")
        print("💬 System response:", result['messages'][-1].content[:100] + "...")
        
        # Provide parameters
        print("\n📝 Demo 3: Providing parameters")
        result2 = workflow.add_user_input("Generate report for Bob, make it quarterly", "demo2")
        
        if result2.get("status") == WorkflowStatus.COMPLETED.value:
            print("✅ Success! Workflow completed after parameter collection")
        else:
            print(f"⚠️ Status: {result2.get('status')}")
    elif result.get("status") == WorkflowStatus.COLLECTING_PARAMS.value:
        print("✅ Success! System identified missing parameters and is ready to collect them")
        if result.get("messages"):
            print("💬 Latest message:", result['messages'][-1].content[:100] + "...")
        
        # Provide parameters  
        print("\n📝 Demo 3: Providing parameters")
        result2 = workflow.add_user_input("Generate report for Bob, make it quarterly", "demo2")
        
        if result2.get("status") == WorkflowStatus.COMPLETED.value:
            print("✅ Success! Workflow completed after parameter collection")
        else:
            print(f"⚠️ Status: {result2.get('status')}")
    else:
        print(f"⚠️ Unexpected status: {result.get('status')}")
        if result.get("messages"):
            print(f"💬 Response: {result['messages'][-1].content[:100]}")
    
    # Run comprehensive tests
    print(f"\n{'=' * 80}")
    print("🧪 Running Enhanced Comprehensive Tests")
    print("=" * 80)
    test_results = run_enhanced_tests()
    print(f"\n{'=' * 80}")
    print("🎉 Enhanced Workflow Testing Completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()