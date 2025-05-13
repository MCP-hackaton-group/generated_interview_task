import json
import requests
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API endpoint configuration
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 5000
SERVER_URL = os.getenv("SERVER_URL", f"http://{DEFAULT_HOST}:{DEFAULT_PORT}")
GENERATE_ENDPOINT = f"{SERVER_URL}/generate-assignment"

def load_json_file(file_path):
    """Load JSON data from a file."""
    clean_path = file_path.strip('"\'')
    try:
        with open(clean_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File not found - {clean_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file - {clean_path}")
        sys.exit(1)
    except OSError as e:
        print(f"Error opening file: {e}")
        print(f"Path: '{clean_path}'")
        sys.exit(1)

def generate_assignment(jira_tasks_file, prompt_file, template_repo_file):
    """Generate a technical home assignment using the API."""
    jira_tasks = load_json_file(jira_tasks_file)
    prompt_data = load_json_file(prompt_file)
    template_repo = load_json_file(template_repo_file)
    
    payload = {
        "jiraTasks": jira_tasks,
        "prompt": prompt_data,
        "templateRepo": template_repo
    }
    
    try:
        response = requests.post(GENERATE_ENDPOINT, json=payload)
        
        if response.status_code == 200:
            assignment_data = response.json()
            return assignment_data
        else:
            error_message = response.json().get('error', 'Unknown error')
            print(f"Error: API request failed with status code {response.status_code}: {error_message}")
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to connect to the API server: {e}")
        sys.exit(1)

def save_assignment(assignment_data, output_file):
    """Save the generated assignment to a file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(assignment_data, file, indent=2)
        print(f"Assignment successfully saved to {output_file}")
    except Exception as e:
        print(f"Error: Failed to save assignment: {e}")
        sys.exit(1)

def display_assignment(assignment_data):
    """Display the assignment data in a formatted way."""
    print("\n=== GENERATED HOME ASSIGNMENT ===\n")
    
    print(f"Title: {assignment_data.get('title', 'N/A')}")
    print(f"Description: {assignment_data.get('description', 'N/A')}")
    
    print("\nRequired Tasks:")
    for i, task in enumerate(assignment_data.get('tasks', []), 1):
        print(f"  {i}. {task}")
    
    print("\nTechnologies and Tools:")
    for tech in assignment_data.get('technologies', []):
        print(f"  - {tech}")
    
    print("\nEvaluation Criteria:")
    for criterion in assignment_data.get('evaluationCriteria', []):
        print(f"  - {criterion}")
    
    print("\nSubmission Instructions:")
    print(assignment_data.get('submissionInstructions', 'N/A'))

def main():
    """Main function to handle command line arguments and generate the assignment."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate a technical home assignment for developer candidates.')
    parser.add_argument('--jira', help='Path to the Jira tasks JSON file')
    parser.add_argument('--prompt', help='Path to the prompt JSON file')
    parser.add_argument('--template', help='Path to the template repository JSON file')
    parser.add_argument('--output', help='Path to save the generated assignment JSON file')
    parser.add_argument('--display', action='store_true', help='Display the generated assignment in the console')
    
    args = parser.parse_args()
    
    jira_file = args.jira
    if not jira_file:
        jira_file = input("Enter path to Jira tasks JSON file: ").strip()
    
    prompt_file = args.prompt
    if not prompt_file:
        prompt_file = input("Enter path to prompt JSON file: ").strip()
    
    template_file = args.template
    if not template_file:
        template_file = input("Enter path to template repository JSON file: ").strip()
    
    output_file = args.output
    if not output_file and not args.display:
        save_output = input("Save output to file? (y/n): ").lower().strip()
        if save_output.startswith('y'):
            output_file = input("Enter output file path: ").strip()
    
    print("Generating technical home assignment...")
    assignment_data = generate_assignment(jira_file, prompt_file, template_file)
    
    if output_file:
        save_assignment(assignment_data, output_file)
    
    if args.display or not output_file:
        display_assignment(assignment_data)

if __name__ == "__main__":
    main()
