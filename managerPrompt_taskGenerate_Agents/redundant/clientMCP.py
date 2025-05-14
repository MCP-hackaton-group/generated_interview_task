
import requests
import argparse
import sys
import json
from dotenv import load_dotenv
import os

load_dotenv()

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 5000
SERVER_URL = os.getenv("SERVER_URL", f"http://{DEFAULT_HOST}:{DEFAULT_PORT}")

def check_server_health(server_url):
    """Check if the MCP server is running"""
    try:
        response = requests.get(f"{server_url}/health")
        if response.status_code == 200:
            return True
        return False
    except requests.exceptions.RequestException:
        return False

def send_prompt(server_url, message, session_id=None):
    """Send a prompt to the MCP server and get a response"""
    try:
        payload = {
            "message": message
        }
        
        if session_id:
            payload["session_id"] = session_id
            
        response = requests.post(
            f"{server_url}/prompt",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_message = response.json().get("error", "Unknown error")
            return {"error": f"Error: {response.status_code} - {error_message}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {e}"}

def interactive_mode(server_url):
    """Interactive conversation mode with the MCP server"""
    print("\n=================================================")
    print("   Manager Prompt Agent - Job Requirements Tool   ")
    print("=================================================")
    print("\nThis tool will help you create job requirements through a QUICK conversation.")
    print("You'll provide initial information, answer ONE round of follow-up questions,")
    print("and then the system will automatically generate the final JSON.")
    print("\n*** ONLY 2 ROUNDS OF CONVERSATION! ***")
    print("\nPlease include information about:")
    print("  - Role details (title, level, focus areas)")
    print("  - Required and preferred skills")
    print("  - Assignment details (difficulty, time required)")
    print("\nType 'exit', 'quit', or press Ctrl+C to end the conversation.")
    print("=================================================")
    
    session_id = None
    json_data = None
    round_number = 0
    
    try:
        # Start the conversation
        initial_prompt = input("\n[INITIAL INPUT] What kind of technical assignment are you looking to create? ")
        
        print("\nProcessing...")
        
        # Send the initial prompt
        response_data = send_prompt(server_url, initial_prompt)
        
        if "error" in response_data:
            print(f"Error: {response_data.get('error')}")
            return
            
        session_id = response_data.get("session_id")
        assistant_msg = response_data.get("answer", "")
        is_complete = response_data.get("complete", False)
        round_number = response_data.get("round", 0)
        
        # Display round information
        print(f"\n[ROUND {round_number}] Agent: {assistant_msg}")
        
        # Continue the conversation until we have complete information or reach round 2
        while not is_complete and round_number < 2:
            round_number += 1
            user_input = input(f"\n[ROUND {round_number}] You: ")
            
            if user_input.lower() in ("exit", "quit"):
                print("Goodbye!")
                break
                
            print("\nProcessing...")
            response_data = send_prompt(server_url, user_input, session_id)
            
            if "error" in response_data:
                print(f"Error: {response_data.get('error')}")
                round_number -= 1  # Revert the round increment if there was an error
                continue
                
            assistant_msg = response_data.get("answer", "")
            is_complete = response_data.get("complete", False)
            current_round = response_data.get("round", round_number)
            
            if current_round >= 2:
                print("\n[FINAL RESPONSE] Agent is generating the complete JSON...")
            
            print(f"\n[ROUND {current_round}] Agent: {assistant_msg}")
            
            # If we've reached round 2, the conversation is over
            if current_round >= 2:
                # Try to parse as JSON even if is_complete flag isn't set
                try:
                    json_data = json.loads(assistant_msg.strip())
                    is_complete = True
                except json.JSONDecodeError:
                    pass
                break
        
        # If we have JSON data, ask if the user wants to save it
        if is_complete and assistant_msg.strip().startswith('{'):
            try:
                json_data = json.loads(assistant_msg.strip())
                print("\n=================================================")
                print("   Job Requirements Complete!   ")
                print("=================================================")
                print("\nHere's the structured information I've gathered:")
                print(json.dumps(json_data, indent=2))
                
                save = input("\nWould you like to save this to a file? (y/n): ").lower().strip()
                if save.startswith('y'):
                    filename = input("Enter filename (default: manager_prompt.json): ").strip() or "manager_prompt.json"
                    with open(filename, 'w') as f:
                        json.dump(json_data, f, indent=2)
                    print(f"Successfully saved to {filename}")
            except json.JSONDecodeError:
                print("\nFailed to parse JSON response. Please try again.")
                
    except KeyboardInterrupt:
        print("\nGoodbye!")

def main():
    parser = argparse.ArgumentParser(description="Client for the MCP (Model Context Protocol) server")
    parser.add_argument("-s", "--server", default=SERVER_URL, 
                        help=f"URL of the MCP server (default: {SERVER_URL})")
    parser.add_argument("-m", "--message", 
                        help="Message to send to the MCP server (if not provided, interactive mode will be used)")
    
    args = parser.parse_args()
    server_url = args.server
    
    if not check_server_health(server_url):
        print(f"Error: Could not connect to MCP server at {server_url}")
        print("Make sure the server is running and try again.")
        sys.exit(1)
    
    if args.message:
        response_data = send_prompt(server_url, args.message)
        if "error" in response_data:
            print(f"Error: {response_data.get('error')}")
        else:
            print(f"MCP Response: {response_data.get('answer', '')}")
    else:
        interactive_mode(server_url)

if __name__ == "__main__":
    main()