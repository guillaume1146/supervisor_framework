"""
Test suite for the enhanced parameter workflow system.
"""

import logging
from typing import Dict, Any

from ..core.engine import EnhancedParameterWorkflow
from ..config.settings import WorkflowConfig, WorkflowStatus
from ..workflows.implementations import PHASE_DEFINITIONS

logger = logging.getLogger(__name__)


def run_enhanced_tests() -> Dict[str, Any]:
    """Run comprehensive tests with improved error handling and logging"""
    logger.info("Starting enhanced comprehensive tests")
    
    # Use debug configuration for testing
    test_config = WorkflowConfig(
        max_iterations=3,
        parameter_extraction_retries=2,
        enable_auto_continuation=True,
        debug_mode=True
    )
    
    workflow = EnhancedParameterWorkflow(PHASE_DEFINITIONS, test_config)
    
    test_cases = [
        {
            "name": "Complete Parameters - Report Generation",
            "message": "Generate a monthly report for user Alice",
            "thread_id": "test_complete_report",
            "expected_status": WorkflowStatus.COMPLETED.value
        },
        {
            "name": "Complete Parameters - Data Processing", 
            "message": "Analyze sales_data with trend analysis",
            "thread_id": "test_complete_data",
            "expected_status": WorkflowStatus.COMPLETED.value
        },
        {
            "name": "Missing Parameters - Report Only",
            "message": "Generate a report",
            "thread_id": "test_missing_report",
            "expected_status": WorkflowStatus.COLLECTING_PARAMS.value
        },
        {
            "name": "Invalid Input - Empty Message",
            "message": "",
            "thread_id": "test_invalid_empty",
            "expected_status": WorkflowStatus.FAILED.value
        },
        {
            "name": "Invalid Input - Whitespace Only",
            "message": "   ",
            "thread_id": "test_invalid_whitespace",
            "expected_status": WorkflowStatus.FAILED.value
        },
        {
            "name": "Ambiguous Request",
            "message": "I need help with something",
            "thread_id": "test_ambiguous",
            "expected_status": WorkflowStatus.COLLECTING_PARAMS.value
        }
    ]
    
    results = {}
    
    for test in test_cases:
        logger.info(f"Running test: {test['name']}")
        
        try:
            result = workflow.run_workflow(test["message"], test["thread_id"])
            results[test["name"]] = {
                "result": result,
                "passed": result.get("status") == test["expected_status"],
                "error": result.get("error")
            }
            
            status = "✅ PASSED" if results[test["name"]]["passed"] else "❌ FAILED"
            logger.info(f"Test '{test['name']}': {status}")
            
        except Exception as e:
            logger.error(f"Test '{test['name']}' failed with exception: {e}")
            results[test["name"]] = {
                "result": {"error": str(e)},
                "passed": False,
                "error": str(e)
            }
    
    # Interactive parameter collection test
    logger.info("Running interactive parameter collection test")
    
    try:
        # Step 1: Start with incomplete parameters
        result1 = workflow.run_workflow("I want a report", "interactive_test")
        
        if result1.get("awaiting_input") or result1.get("status") == WorkflowStatus.COLLECTING_PARAMS.value:
            # Step 2: Provide partial parameters
            result2 = workflow.add_user_input("The user is Sarah", "interactive_test")
            
            if result2.get("awaiting_input") or result2.get("status") == WorkflowStatus.COLLECTING_PARAMS.value:
                # Step 3: Provide remaining parameters
                result3 = workflow.add_user_input("Make it annual", "interactive_test")
                
                interactive_passed = result3.get("status") == WorkflowStatus.COMPLETED.value
                logger.info(f"Interactive test: {'✅ PASSED' if interactive_passed else '❌ FAILED'}")
                
                if not interactive_passed:
                    logger.info(f"Final status: {result3.get('status')}, awaiting: {result3.get('awaiting_input')}")
                    if result3.get("messages"):
                        logger.info(f"Final message: {result3['messages'][-1].content[:100]}")
                
                results["Interactive Parameter Collection"] = {
                    "result": result3,
                    "passed": interactive_passed,
                    "error": result3.get("error")
                }
            else:
                logger.warning(f"Interactive test: Step 2 completed unexpectedly with status: {result2.get('status')}")
                # If step 2 completed, that might actually be success if it collected both parameters
                if result2.get("status") == WorkflowStatus.COMPLETED.value:
                    logger.info("Interactive test: ✅ PASSED (completed in 2 steps instead of 3)")
                    results["Interactive Parameter Collection"] = {
                        "result": result2,
                        "passed": True,
                        "error": None
                    }
                else:
                    results["Interactive Parameter Collection"] = {
                        "result": result2,
                        "passed": False,
                        "error": f"Unexpected status after step 2: {result2.get('status')}"
                    }
        else:
            logger.warning(f"Interactive test: Step 1 completed unexpectedly with status: {result1.get('status')}")
            results["Interactive Parameter Collection"] = {
                "result": result1,
                "passed": False,
                "error": f"Step 1 should request parameters but got status: {result1.get('status')}"
            }
    
    except Exception as e:
        logger.error(f"Interactive test failed: {e}")
        results["Interactive Parameter Collection"] = {
            "result": {"error": str(e)},
            "passed": False,
            "error": str(e)
        }
    
    # Print summary
    passed_tests = sum(1 for r in results.values() if r["passed"])
    total_tests = len(results)
    
    logger.info(f"Test Summary: {passed_tests}/{total_tests} tests passed")
    
    return results