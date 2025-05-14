#!/usr/bin/env python3
"""
Integration test for the complete workflow.
This tests the integration of Jira extractor, manager prompt, and task generator.
"""

import json
import sys
import os
from datetime import datetime
from agents_workflow import main_agents_workflow

def run_test():
    """Run a test of the entire workflow"""
    print("=== Testing Agents Workflow ===\n")
    
    # Create results directory
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Test cases
    test_cases = [
        {
            "name": "Backend Development Test",
            "input": {
                "tasks_description": "backend development, user authentication, database design, api integration",
                "language": "python, Flask, PostgreSQL"
            }
        },
        {
            "name": "Frontend Development Test",
            "input": {
                "tasks_description": "frontend development, UI components, form validation, data visualization",
                "language": "javascript, React, CSS, HTML"
            }
        },
        {
            "name": "Full Stack Development Test",
            "input": {
                "tasks_description": "full stack development, user registration, dashboard UI, RESTful API",
                "language": "Node.js, Express, MongoDB, React"
            }
        }
    ]
    
    # Track results
    results = []
    
    # Run each test case
    for idx, test in enumerate(test_cases):
        print(f"\n{'-'*60}")
        print(f"Test #{idx+1}: {test['name']}")
        print(f"{'-'*60}")
        print(f"Input: {json.dumps(test['input'], indent=2)}")
        
        try:
            print(f"\nRunning workflow...")
            result = main_agents_workflow(test['input'])
            print("\n✅ Success! Output summary:")
            
            # Print a summary of the result
            if isinstance(result, dict):
                # Look for common fields in various possible result structures
                title = result.get('title', result.get('assignmentTitle', ''))
                if title:
                    print(f"Title: {title}")
                
                desc_field = next((f for f in ['shortDescription', 'description', 'overview'] if f in result), None)
                if desc_field:
                    desc = result[desc_field]
                    print(f"Description: {desc[:100]}..." if len(desc) > 100 else f"Description: {desc}")
                
                tasks_field = next((f for f in ['requiredTasks', 'tasks', 'assignments'] if f in result), None)
                if tasks_field and isinstance(result[tasks_field], list):
                    print(f"Number of tasks: {len(result[tasks_field])}")
                
                # Save the result to a file
                output_file = f"results/test_{test['name'].replace(' ', '_').lower()}_{timestamp}.json"
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)
                print(f"\nFull output saved to {output_file}")
                
                results.append({
                    "name": test["name"],
                    "passed": True,
                    "file": output_file
                })
            else:
                print(f"⚠️ Unexpected result type: {type(result)}")
                results.append({
                    "name": test["name"],
                    "passed": False,
                    "error": f"Unexpected result type: {type(result)}"
                })
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "name": test["name"],
                "passed": False,
                "error": str(e)
            })
    
    # Print summary
    print(f"\n{'-'*60}")
    print("TEST RESULTS SUMMARY")
    print(f"{'-'*60}")
    
    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed
    
    for result in results:
        status = "✅ PASSED" if result["passed"] else "❌ FAILED"
        print(f"{status} - {result['name']}")
        if not result["passed"] and "error" in result:
            print(f"      Error: {result['error']}")
    
    print(f"\nTests: {len(results)} | Passed: {passed} | Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! The workflow integration is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the results for details.")
    
    return failed

if __name__ == "__main__":
    exit_code = run_test()
    sys.exit(exit_code)
