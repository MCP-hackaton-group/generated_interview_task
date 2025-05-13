
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

def send_prompt(server_url, message):
    """Send a prompt to the MCP server and get a response"""
    try:
        response = requests.post(
            f"{server_url}/prompt",
            json={"message": message},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json().get("answer")
        else:
            error_message = response.json().get("error", "Unknown error")
            return f"Error: {response.status_code} - {error_message}"
    except requests.exceptions.RequestException as e:
        return f"Connection error: {e}"

def interactive_mode(server_url):
    """Interactive conversation mode with the MCP server"""
    print(f"Connected to MCP server at {server_url}")
    print("Type 'exit', 'quit', or Ctrl+C to end the conversation.")
    print("-" * 50)
    
    try:
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ("exit", "quit"):
                print("Goodbye!")
                break
                
            print("\nProcessing...")
            response = send_prompt(server_url, user_input)
            print(f"\nMCP: {response}")
            print("-" * 50)
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
        response = send_prompt(server_url, args.message)
        print(f"MCP Response: {response}")
    else:
        interactive_mode(server_url)

if __name__ == "__main__":
    main()