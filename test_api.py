#!/usr/bin/env python
"""
Test client for the Interview Task Generator API
"""

import requests
import json
import sys
import os
from datetime import datetime

def test_api(task_description, language):
    """Send a test request to the API"""
    url = "http://localhost:5001/user-message"
    
    # Create payload
    payload = {
        "message": {
            "task_description": task_description,
            "language": language
        }
    }
    
    print("\n" + "="*60)
    print(" "*20 + "SENDING API REQUEST")
    print("="*60)
    print(f"\nURL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    # Check if server is running
    try:
        print("\nChecking if server is running...")
        server_check = requests.get(url.replace("/user-message", "/"), timeout=2)
        if server_check.status_code != 200:
            print("Server might be running but not responding correctly.")
    except requests.exceptions.ConnectionError:
        print("\n⚠️ ERROR: Cannot connect to the server!")
        print("  → Make sure the server is running by executing 'run_server.bat'")
        print("  → The server should be accessible at http://localhost:5001")
        return
    except requests.exceptions.Timeout:
        print("\n⚠️ WARNING: Server connection timed out, but will try to send the request anyway.")
    except Exception as e:
        print(f"\n⚠️ WARNING: {str(e)}")
        print("  → Will attempt to send the request anyway.")
    
    try:
        print("\nSending request...")
        response = requests.post(url, json=payload)
        
        # Create results directory if it doesn't exist
        os.makedirs("results", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Success! Response received.")
            
            if 'result' in data:
                # Save the result
                with open(f"results/api_result_{timestamp}.json", "w") as f:
                    json.dump(data['result'], f, indent=2)
                print(f"\nResult saved to: results/api_result_{timestamp}.json")
                
                # Print a summary
                print("\n" + "-"*60)
                print(" "*20 + "RESPONSE SUMMARY")
                print("-"*60)
                
                if isinstance(data['result'], dict):
                    # Try different possible field names
                    title = data['result'].get('title', data['result'].get('assignmentTitle', 
                           data['result'].get('name', 'Untitled Assignment')))
                    print(f"\nTitle: {title}")
                    
                    # Find description field by checking common names
                    desc_field = next((f for f in ['shortDescription', 'description', 'overview', 'summary'] 
                                     if f in data['result']), None)
                    if desc_field:
                        desc = data['result'][desc_field]
                        print(f"Description: {desc[:200]}..." if len(desc) > 200 else f"Description: {desc}")
                    
                    # Find tasks field by checking common names
                    tasks_field = next((f for f in ['requiredTasks', 'tasks', 'assignments', 'requirements'] 
                                      if f in data['result'] and isinstance(data['result'][f], list)), None)
                    if tasks_field:
                        task_count = len(data['result'][tasks_field])
                        print(f"Number of tasks: {task_count}")
                        
                        # Print first few tasks
                        print("\nTasks preview:")
                        for i, task in enumerate(data['result'][tasks_field][:3]):
                            if isinstance(task, dict):
                                task_title = task.get('title', task.get('name', f"Task {i+1}"))
                                print(f"  - {task_title}")
                        
                        if task_count > 3:
                            print(f"  ... and {task_count-3} more tasks")
                    
                    print("\n" + "-"*60)
                    print(f"Full assignment details available in: results/api_result_{timestamp}.json")
            else:
                print("\nResponse (no result found):")
                print(json.dumps(data, indent=2))
        else:
            print(f"\n❌ Error: HTTP {response.status_code}")
            print("-"*60)
            print(response.text)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("-"*60)
        import traceback
        traceback.print_exc()

def main():
    """Main function with command line arguments"""
    if len(sys.argv) > 2:
        task_description = sys.argv[1]
        language = sys.argv[2]
    else:
        print("\nTechnical Interview Task Generator - API Client")
        print("\nEnter task description: ")
        task_description = input().strip()
        if not task_description:
            task_description = "backend development, user authentication, database design, API endpoints"
            print(f"Using default: {task_description}")
        
        print("\nEnter programming languages/frameworks: ")
        language = input().strip()
        if not language:
            language = "Python, FastAPI, PostgreSQL"
            print(f"Using default: {language}")
    
    test_api(task_description, language)

if __name__ == "__main__":
    main()
