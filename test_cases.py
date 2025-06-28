"""
Test cases and examples for the FastAPI chatbot endpoint.
"""

import json
from typing import List, Dict, Any


class ChatbotTestCases:
    """Test cases for the chatbot API"""
    
    @staticmethod
    def get_all_test_cases() -> List[Dict[str, Any]]:
        """Get all test cases for Postman testing"""
        return [
            # Test Case 1: Complete Parameters - Report Generation
            {
                "name": "Complete Parameters - Report Generation",
                "description": "Test with all required parameters provided in one message",
                "requests": [
                    {
                        "step": 1,
                        "method": "POST",
                        "url": "http://localhost:8000/chat",
                        "body": {
                            "message": "Generate a monthly report for Alice"
                        },
                        "expected_status": "completed",
                        "expected_awaiting_input": False
                    }
                ]
            },
            
            # Test Case 2: Complete Parameters - Data Processing
            {
                "name": "Complete Parameters - Data Processing",
                "description": "Test data processing workflow with complete parameters",
                "requests": [
                    {
                        "step": 1,
                        "method": "POST",
                        "url": "http://localhost:8000/chat",
                        "body": {
                            "message": "Analyze sales_data with trend analysis"
                        },
                        "expected_status": "completed",
                        "expected_awaiting_input": False
                    }
                ]
            },
            
            # Test Case 3: Missing Parameters - Interactive Collection
            {
                "name": "Missing Parameters - Interactive Collection",
                "description": "Test interactive parameter collection over multiple messages",
                "requests": [
                    {
                        "step": 1,
                        "method": "POST",
                        "url": "http://localhost:8000/chat",
                        "body": {
                            "message": "Generate a report"
                        },
                        "expected_status": "waiting_input",
                        "expected_awaiting_input": True,
                        "note": "Save session_id from response for next request"
                    },
                    {
                        "step": 2,
                        "method": "POST",
                        "url": "http://localhost:8000/chat",
                        "body": {
                            "message": "The user is Bob",
                            "session_id": "{{SESSION_ID_FROM_STEP_1}}"
                        },
                        "expected_status": "waiting_input",
                        "expected_awaiting_input": True
                    },
                    {
                        "step": 3,
                        "method": "POST",
                        "url": "http://localhost:8000/chat",
                        "body": {
                            "message": "Make it quarterly",
                            "session_id": "{{SESSION_ID_FROM_STEP_1}}"
                        },
                        "expected_status": "completed",
                        "expected_awaiting_input": False
                    }
                ]
            },
            
            # Test Case 4: All-in-One Parameter Collection
            {
                "name": "All-in-One Parameter Collection",
                "description": "Provide all missing parameters in one follow-up message",
                "requests": [
                    {
                        "step": 1,
                        "method": "POST",
                        "url": "http://localhost:8000/chat",
                        "body": {
                            "message": "I want a report"
                        },
                        "expected_status": "waiting_input",
                        "expected_awaiting_input": True
                    },
                    {
                        "step": 2,
                        "method": "POST",
                        "url": "http://localhost:8000/chat",
                        "body": {
                            "message": "Generate report for Sarah, make it annual",
                            "session_id": "{{SESSION_ID_FROM_STEP_1}}"
                        },
                        "expected_status": "completed",
                        "expected_awaiting_input": False
                    }
                ]
            },
            
            # Test Case 5: Invalid Input - Empty Message
            {
                "name": "Invalid Input - Empty Message",
                "description": "Test error handling with empty message",
                "requests": [
                    {
                        "step": 1,
                        "method": "POST",
                        "url": "http://localhost:8000/chat",
                        "body": {
                            "message": ""
                        },
                        "expected_status": "failed",
                        "expected_awaiting_input": False,
                        "note": "Should return validation error"
                    }
                ]
            },
            
            # Test Case 6: Ambiguous Request
            {
                "name": "Ambiguous Request",
                "description": "Test with ambiguous user request",
                "requests": [
                    {
                        "step": 1,
                        "method": "POST",
                        "url": "http://localhost:8000/chat",
                        "body": {
                            "message": "I need help with something"
                        },
                        "expected_status": "waiting_input",
                        "expected_awaiting_input": True
                    }
                ]
            },
            
            # Test Case 7: Data Processing Workflow
            {
                "name": "Data Processing - Missing Parameters",
                "description": "Test data processing with missing parameters",
                "requests": [
                    {
                        "step": 1,
                        "method": "POST",
                        "url": "http://localhost:8000/chat",
                        "body": {
                            "message": "Analyze my data"
                        },
                        "expected_status": "waiting_input",
                        "expected_awaiting_input": True
                    },
                    {
                        "step": 2,
                        "method": "POST",
                        "url": "http://localhost:8000/chat",
                        "body": {
                            "message": "Use user_metrics data source for performance analysis",
                            "session_id": "{{SESSION_ID_FROM_STEP_1}}"
                        },
                        "expected_status": "completed",
                        "expected_awaiting_input": False
                    }
                ]
            }
        ]
    
    @staticmethod
    def print_postman_instructions():
        """Print instructions for testing with Postman"""
        print("=" * 80)
        print("📬 POSTMAN TESTING INSTRUCTIONS")
        print("=" * 80)
        print()
        print("1. 🚀 Start the FastAPI server:")
        print("   python main_fastapi.py")
        print()
        print("2. 🌐 Test the health endpoint:")
        print("   GET http://localhost:8000/health")
        print()
        print("3. 💬 Test chat endpoint:")
        print("   POST http://localhost:8000/chat")
        print("   Content-Type: application/json")
        print()
        print("4. 📋 Additional endpoints:")
        print("   GET  http://localhost:8000/sessions          - List all sessions")
        print("   GET  http://localhost:8000/sessions/{id}     - Get session info")
        print("   DEL  http://localhost:8000/sessions/{id}     - Clear session")
        print("   GET  http://localhost:8000/docs             - API documentation")
        print()
        print("5. 🧪 Test Cases:")
        
        test_cases = ChatbotTestCases.get_all_test_cases()
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n   📝 Test Case {i}: {test_case['name']}")
            print(f"      {test_case['description']}")
            
            for request in test_case['requests']:
                print(f"\n      Step {request['step']}:")
                print(f"      {request['method']} {request['url']}")
                print(f"      Body: {json.dumps(request['body'], indent=6)}")
                print(f"      Expected Status: {request['expected_status']}")
                print(f"      Expected Awaiting Input: {request['expected_awaiting_input']}")
                if 'note' in request:
                    print(f"      Note: {request['note']}")
        
        print(f"\n{'=' * 80}")
        print("🔧 IMPORTANT NOTES:")
        print("=" * 80)
        print("• Replace {{SESSION_ID_FROM_STEP_1}} with actual session_id from step 1 response")
        print("• Each test case should be run independently or clear sessions between tests")
        print("• Check response status codes: 200 for success, 422 for validation errors")
        print("• Monitor server logs for detailed workflow execution information")
        print("• Use Postman's 'Tests' tab to automatically extract session_id for multi-step tests")
        print()

    @staticmethod
    def get_postman_collection() -> Dict[str, Any]:
        """Generate a Postman collection for easy import"""
        collection = {
            "info": {
                "name": "Enhanced Workflow Chatbot API",
                "description": "Test collection for the Enhanced Workflow Chatbot API",
                "version": "1.0.0"
            },
            "variable": [
                {
                    "key": "base_url",
                    "value": "http://localhost:8000",
                    "type": "string"
                }
            ],
            "item": []
        }
        
        # Add health check
        collection["item"].append({
            "name": "Health Check",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/health",
                    "host": ["{{base_url}}"],
                    "path": ["health"]
                }
            }
        })
        
        # Add test cases
        test_cases = ChatbotTestCases.get_all_test_cases()
        for test_case in test_cases:
            folder = {
                "name": test_case["name"],
                "item": []
            }
            
            for request in test_case["requests"]:
                item = {
                    "name": f"Step {request['step']}",
                    "request": {
                        "method": request["method"],
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps(request["body"], indent=2)
                        },
                        "url": {
                            "raw": request["url"],
                            "protocol": "http",
                            "host": ["localhost:8000"],
                            "path": ["chat"]
                        }
                    }
                }
                
                if request["step"] > 1:
                    # Add test script to extract session_id
                    item["event"] = [
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    "if (pm.response.code === 200) {",
                                    "    var response = pm.response.json();",
                                    "    if (response.session_id) {",
                                    "        pm.collectionVariables.set('session_id', response.session_id);",
                                    "    }",
                                    "}"
                                ]
                            }
                        }
                    ]
                
                folder["item"].append(item)
            
            collection["item"].append(folder)
        
        return collection