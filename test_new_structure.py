"""
Test script to verify the new modular structure works correctly
"""

from dotenv import load_dotenv

load_dotenv()

def test_imports():
    """Test that all new imports work correctly"""
    print("🧪 Testing new modular imports...")
    
    try:
        # Test main imports (backward compatible)
        from workflow_system import EnhancedParameterWorkflow, WorkflowConfig, PHASE_DEFINITIONS
        print("   ✅ Main imports work")
        
        # Test utils imports
        from workflow_system.utils import normalize_currency, validate_date_format
        print("   ✅ Utils imports work")
        
        # Test phase-specific imports
        from workflow_system.phases.phase1_financial_input import FinancialInputValidationParams
        print("   ✅ Phase-specific imports work")
        
        # Test registry imports
        from workflow_system.workflows import get_workflow_registry
        print("   ✅ Registry imports work")
        
        # Test phase count
        print(f"   ✅ {len(PHASE_DEFINITIONS)} phases loaded successfully")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False


def test_functionality():
    """Test that core functionality still works"""
    print("\n🔧 Testing core functionality...")
    
    try:
        # Test utils
        from workflow_system.utils import normalize_currency
        result = normalize_currency("50k")
        print(f"   ✅ Currency normalization: '50k' → '{result}'")
        
        # Test workflow creation
        from workflow_system import EnhancedParameterWorkflow, WorkflowConfig, PHASE_DEFINITIONS
        config = WorkflowConfig(debug_mode=True)
        workflow = EnhancedParameterWorkflow(PHASE_DEFINITIONS, config)
        print(f"   ✅ Workflow created with {len(PHASE_DEFINITIONS)} phases")
        
        # Test registry
        from workflow_system.workflows import get_workflow_registry
        registry = get_workflow_registry()
        phases = registry.list_phase_names()
        print(f"   ✅ Registry contains phases: {phases}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Functionality error: {e}")
        return False


if __name__ == "__main__":
    print("🔍 Testing New Modular Structure")
    print("=" * 40)
    
    import_success = test_imports()
    functionality_success = test_functionality()
    
    if import_success and functionality_success:
        print("\n🎉 All tests passed! New modular structure is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the setup.")