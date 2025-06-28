"""
Test cases for Phase 1: Financial Input Validation workflow using new modular structure
"""
from dotenv import load_dotenv

load_dotenv()

# Updated imports using new modular structure
from workflow_system import EnhancedParameterWorkflow, WorkflowConfig, WorkflowStatus
from workflow_system.workflows import PHASE_DEFINITIONS  # Auto-loaded from registry
from workflow_system.phases.phase1_financial_input import FinancialInputValidationParams


def test_phase1_complete_input():
    """Test Phase 1 with complete input"""
    print("🧪 Testing Phase 1 with new modular structure...")
    print(f"📋 Available phases: {[p.name for p in PHASE_DEFINITIONS]}")
    
    config = WorkflowConfig(debug_mode=True)
    workflow = EnhancedParameterWorkflow(PHASE_DEFINITIONS, config)
    
    test_message = """
    I need to analyze my Aviva SIPP valued at £125,000 as of 15/03/2024. 
    I contribute £5,000 annually and I'm 45 years old. 
    I'm not taking any income withdrawals and plan to invest for 20 years until retirement.
    """
    
    result = workflow.run_workflow(test_message, "test_phase1_complete")
    
    print("=== Phase 1 Complete Input Test ===")
    print(f"Status: {result.get('status')}")
    if result.get('messages'):
        print(f"Response: {result['messages'][-1].content}")
    
    return result


def test_phase1_partial_input():
    """Test Phase 1 with partial input"""
    config = WorkflowConfig(debug_mode=True)
    workflow = EnhancedParameterWorkflow(PHASE_DEFINITIONS, config)
    
    test_message = "I have a pension worth £50,000 and I contribute £3,000 per year"
    
    result = workflow.run_workflow(test_message, "test_phase1_partial")
    
    print("\n=== Phase 1 Partial Input Test ===")
    print(f"Status: {result.get('status')}")
    if result.get('messages'):
        print(f"Response: {result['messages'][-1].content[:200]}...")
    
    return result


def test_phase1_interactive_completion():
    """Test Phase 1 interactive parameter collection"""
    config = WorkflowConfig(debug_mode=True)
    workflow = EnhancedParameterWorkflow(PHASE_DEFINITIONS, config)
    
    # Step 1: Start with minimal info
    result1 = workflow.run_workflow("I want to analyze my investment", "test_phase1_interactive")
    
    print("\n=== Phase 1 Interactive Test - Step 1 ===")
    print(f"Status: {result1.get('status')}")
    print("System requesting parameters...")
    
    # Step 2: Provide some information
    result2 = workflow.add_user_input(
        "It's a Standard Life pension worth £75,000 as of today", 
        "test_phase1_interactive"
    )
    
    print("\n=== Phase 1 Interactive Test - Step 2 ===")
    print(f"Status: {result2.get('status')}")
    
    # Step 3: Complete the information
    result3 = workflow.add_user_input(
        "I contribute £4,000 annually and I'm 50 years old", 
        "test_phase1_interactive"
    )
    
    print("\n=== Phase 1 Interactive Test - Step 3 ===")
    print(f"Status: {result3.get('status')}")
    
    # Step 4: Final missing parameters
    result4 = workflow.add_user_input(
        "I'm not taking any income withdrawals and plan to invest for 15 years", 
        "test_phase1_interactive"
    )
    
    print("\n=== Phase 1 Interactive Test - Step 4 ===")
    print(f"Status: {result4.get('status')}")
    if result4.get('messages'):
        print("Final result received!")
        if "COMPLETED" in result4['messages'][-1].content:
            print("✅ Interactive collection completed successfully!")
    
    return result4


def test_utils_functionality():
    """Test the new utilities functionality"""
    print("\n=== Testing New Utils Functionality ===")
    
    # Test normalizers
    from workflow_system.utils import normalize_currency, normalize_date, normalize_product_type
    
    print("Testing normalizers:")
    print(f"Currency '50k' → {normalize_currency('50k')}")
    print(f"Date 'today' → {normalize_date('today')}")
    print(f"Product 'sipp' → {normalize_product_type('sipp')}")
    
    # Test validators
    from workflow_system.utils import validate_currency_amount, validate_date_format
    
    print("\nTesting validators:")
    print(f"Valid currency '£50000': {validate_currency_amount('£50000')}")
    print(f"Valid date '15/03/2024': {validate_date_format('15/03/2024')}")
    
    # Test calculators
    from workflow_system.utils import calculate_data_quality_score
    
    test_data = {
        'field1': 'value1',
        'field2': 'value2', 
        'field3': None,
        'field4': 'Not specified'
    }
    score = calculate_data_quality_score(test_data)
    print(f"\nData quality score for test data: {score}/100")


def test_phase_registry():
    """Test the new phase registry functionality"""
    print("\n=== Testing Phase Registry ===")
    
    from workflow_system.workflows import get_workflow_registry
    
    registry = get_workflow_registry()
    
    print(f"Registered phases: {registry.list_phase_names()}")
    
    # Test getting specific phase
    phase1 = registry.get_phase("financial_input_validation")
    if phase1:
        print(f"Phase 1 found: {phase1.description}")
    
    print(f"Total phases registered: {len(registry.get_all_phases())}")


if __name__ == "__main__":
    print("🧪 Testing Phase 1: Financial Input Validation Workflow (Modular Structure v2.0)")
    print("=" * 80)
    
    # Test utilities first
    test_utils_functionality()
    test_phase_registry()
    
    # Run workflow tests
    test_phase1_complete_input()
    test_phase1_partial_input()
    test_phase1_interactive_completion()
    
    print("\n" + "=" * 80)
    print("✅ All Phase 1 tests completed with new modular structure!")