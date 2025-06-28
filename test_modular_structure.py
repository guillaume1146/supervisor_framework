"""
Test script for the new modular workflow structure
"""

import logging
from workflow_system import EnhancedParameterWorkflow, WorkflowConfig
from workflow_system.workflows import PHASE_DEFINITIONS, get_workflow_registry

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_modular_imports():
    """Test that all modular imports work correctly"""
    print("🧪 Testing Modular Imports...")
    
    try:
        # Test main imports
        from workflow_system import EnhancedParameterWorkflow, WorkflowConfig, WorkflowStatus
        print("✅ Main imports: OK")
        
        # Test workflow registry
        from workflow_system.workflows import get_workflow_registry, PHASE_DEFINITIONS
        registry = get_workflow_registry()
        print(f"✅ Workflow registry: {len(registry.get_all_phases())} phases loaded")
        
        # Test utils imports
        from workflow_system.utils import normalize_currency, validate_date_format
        print("✅ Utils imports: OK")
        
        # Test individual phase imports
        from workflow_system.phases.phase1_financial_input import FinancialInputValidationParams
        from workflow_system.phases.report_generation import GenerateReportParams
        from workflow_system.phases.data_processing import ProcessDataParams
        print("✅ Phase imports: OK")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_workflow_initialization():
    """Test workflow initialization with modular structure"""
    print("\n🧪 Testing Workflow Initialization...")
    
    try:
        config = WorkflowConfig(debug_mode=True)
        workflow = EnhancedParameterWorkflow(PHASE_DEFINITIONS, config)
        
        print(f"✅ Workflow initialized with {len(workflow.phase_definitions)} phases:")
        for name, definition in workflow.phase_definitions.items():
            print(f"   📋 {name}: {definition.description}")
        
        return True
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False


def test_phase1_complete():
    """Test Phase 1 with complete input"""
    print("\n🧪 Testing Phase 1 - Complete Input...")
    
    try:
        config = WorkflowConfig(debug_mode=True)
        workflow = EnhancedParameterWorkflow(PHASE_DEFINITIONS, config)
        
        test_message = """
        I need to analyze my Aviva SIPP valued at £125,000 as of 15/03/2024. 
        I contribute £5,000 annually and I'm 45 years old. 
        I'm not taking any income withdrawals and plan to invest for 20 years until retirement.
        """
        
        result = workflow.run_workflow(test_message, "test_modular_complete")
        
        print(f"✅ Status: {result.get('status')}")
        if result.get('status') == 'completed':
            print("✅ Phase 1 workflow completed successfully")
            return True
        else:
            print(f"⚠️ Unexpected status: {result.get('status')}")
            return False
            
    except Exception as e:
        print(f"❌ Phase 1 test error: {e}")
        return False


def test_utils_functionality():
    """Test utility functions"""
    print("\n🧪 Testing Utility Functions...")
    
    try:
        from workflow_system.utils import (
            normalize_currency, normalize_date, normalize_product_type,
            validate_currency_amount, validate_date_format,
            calculate_data_quality_score
        )
        
        # Test normalizers
        currency_result = normalize_currency("50k")
        date_result = normalize_date("15/03/2024")
        product_result = normalize_product_type("sipp")
        
        print(f"✅ normalize_currency('50k') = {currency_result}")
        print(f"✅ normalize_date('15/03/2024') = {date_result}")
        print(f"✅ normalize_product_type('sipp') = {product_result}")
        
        # Test validators
        is_valid_currency = validate_currency_amount("£50,000")
        is_valid_date = validate_date_format("15/03/2024")
        
        print(f"✅ validate_currency_amount('£50,000') = {is_valid_currency}")
        print(f"✅ validate_date_format('15/03/2024') = {is_valid_date}")
        
        # Test calculators
        test_data = {"field1": "value1", "field2": "value2", "field3": None}
        quality_score = calculate_data_quality_score(test_data)
        print(f"✅ calculate_data_quality_score() = {quality_score}")
        
        return True
    except Exception as e:
        print(f"❌ Utils test error: {e}")
        return False


def run_all_tests():
    """Run all modular structure tests"""
    print("🚀 Testing New Modular Workflow Structure")
    print("=" * 50)
    
    tests = [
        ("Modular Imports", test_modular_imports),
        ("Workflow Initialization", test_workflow_initialization), 
        ("Phase 1 Complete Test", test_phase1_complete),
        ("Utils Functionality", test_utils_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'=' * 50}")
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Modular structure is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)