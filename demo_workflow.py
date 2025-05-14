#!/usr/bin/env python3
"""
Demonstration script for the complete workflow with step-by-step visualization
"""

import json
import sys
import os
from datetime import datetime
from jira_extractor.jira_extractor_agent import main as jira_extractor_agent
from managerPrompt_taskGenerate_Agents.mcpServer_managerPrompt import generate_manager_prompt_conversation
from managerPrompt_taskGenerate_Agents.mcpServer_taskGenerate import generate_home_assignment

def print_header(title):
    """Print a pretty header for output sections"""
    print("\n" + "="*60)
    print(" " * ((60 - len(title)) // 2) + title)
    print("="*60 + "\n")

def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))
    print("\n" + "-"*60)

def demo_workflow():
    """Run a step-by-step demonstration of the workflow"""
    # Create a results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print_header("WORKFLOW DEMONSTRATION")
    print("This script will demonstrate each step of the interview task generation workflow")
    print("Results will be saved to the 'results' directory")
    
    # Get user input or use default
    print("\nEnter task description (or press Enter for default): ")
    tasks_description = input().strip()
    if not tasks_description:
        tasks_description = "backend development, user authentication, database design, API endpoints, unit testing"
        print(f"Using default: {tasks_description}")
    
    print("\nEnter programming languages/frameworks (or press Enter for default): ")
    languages = input().strip()
    if not languages:
        languages = "Python, FastAPI, PostgreSQL, React"
        print(f"Using default: {languages}")
    
    # Create input JSON
    input_data = {
        "tasks_description": tasks_description,
        "language": languages
    }
    
    # Save input
    with open(f"results/input_{timestamp}.json", "w") as f:
        json.dump(input_data, f, indent=2)
    
    print_header("STEP 1: JIRA EXTRACTOR AGENT")
    print("Extracting relevant Jira tasks based on the input...")
    
    try:
        jira_data = jira_extractor_agent(input_data)
        print("\nJira Extractor Output:")
        print_json(jira_data)
        
        # Save Jira output
        with open(f"results/jira_{timestamp}.json", "w") as f:
            json.dump(jira_data, f, indent=2)
            
        # Extract information for manager prompt
        jira_tasks = []
        tech_stack = []
        skills = []
        
        # Handle different possible formats of Jira response
        if isinstance(jira_data, dict):
            if "tasks" in jira_data and isinstance(jira_data["tasks"], list):
                jira_tasks = jira_data["tasks"]
            elif "issues" in jira_data and isinstance(jira_data["issues"], list):
                jira_tasks = [task.get("title", task.get("summary", "")) for task in jira_data["issues"] if isinstance(task, dict)]
            
            # Extract tech stack
            if "tech_stack" in jira_data:
                tech_stack_data = jira_data["tech_stack"]
                if isinstance(tech_stack_data, dict):
                    for key, values in tech_stack_data.items():
                        if isinstance(values, list):
                            tech_stack.extend(values)
                elif isinstance(tech_stack_data, list):
                    tech_stack = tech_stack_data
            
            # Extract skills
            if "team_skills" in jira_data:
                skills_data = jira_data["team_skills"]
                if isinstance(skills_data, dict):
                    for key, values in skills_data.items():
                        if isinstance(values, list):
                            skills.extend(values)
                elif isinstance(skills_data, list):
                    skills = skills_data
            elif "skills" in jira_data and isinstance(jira_data["skills"], list):
                skills = jira_data["skills"]
        
        # Fallback to task description if no tasks found
        if not jira_tasks:
            jira_tasks = [item.strip() for item in tasks_description.split(',') if item.strip()]
        
        print_header("STEP 2: MANAGER PROMPT AGENT")
        print("Generating structured job requirements using the manager prompt agent...")
        
        # Create messages for manager prompt
        initial_message = f"I need to create a technical assignment for {languages} " \
                       f"focusing on {tasks_description}. " \
                       f"Based on the following tasks: {', '.join(jira_tasks[:3] if jira_tasks else ['general development tasks'])}"
                       
        second_message = f"The technical stack should include {', '.join(tech_stack[:5] if tech_stack else languages.split(','))} " \
                      f"and should test skills in {', '.join(skills[:5] if skills else jira_tasks[:3])}"
        
        print("\nPrompt Input:")
        print(f"Message 1: {initial_message}")
        print(f"Message 2: {second_message}")
        
        # Generate manager prompt
        try:
            manager_json = generate_manager_prompt_conversation([initial_message, second_message])
            print("\nManager Prompt Output:")
            print_json(manager_json)
            
            # Save manager prompt output
            with open(f"results/manager_prompt_{timestamp}.json", "w") as f:
                json.dump(manager_json, f, indent=2)
                
            print_header("STEP 3: TASK GENERATION")
            print("Generating the complete home assignment based on requirements...")
            
            # Create simple template repo structure
            template_repo = {
                "repository": {
                    "name": "technical-interview-template",
                    "description": f"Template for {manager_json['role'].get('title', 'Developer')} interview assignment"
                },
                "structure": {
                    "frontend": {
                        "technology": languages,
                        "files": [{"path": "src/App.js", "description": "Main application component"}]
                    },
                    "backend": {
                        "technology": languages,
                        "files": [{"path": "server/index.js", "description": "Server entry point"}]
                    },
                    "documentation": {
                        "files": [{"path": "README.md", "description": "Project documentation"}]
                    }
                }
            }
            
            # Build the complete input for home assignment generation
            generation_input = {
                "jira_tasks": jira_data,
                "prompt_data": manager_json,
                "template_repo": template_repo
            }
            
            # Generate home assignment
            home_assignment = generate_home_assignment(generation_input)
            print("\nHome Assignment Output:")
            print_json(home_assignment)
            
            # Save final output
            with open(f"results/assignment_{timestamp}.json", "w") as f:
                json.dump(home_assignment, f, indent=2)
                
            print_header("WORKFLOW COMPLETE")
            print(f"All results have been saved to the 'results' directory with timestamp {timestamp}")
            print("You can find the following files:")
            print(f"- input_{timestamp}.json - Your original input")
            print(f"- jira_{timestamp}.json - Jira task data")
            print(f"- manager_prompt_{timestamp}.json - Generated job requirements")
            print(f"- assignment_{timestamp}.json - Final assignment")
            
        except Exception as e:
            print(f"\nError in manager prompt generation: {e}")
            print("Workflow demonstration stopped at Step 2")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"\nError in Jira extraction: {e}")
        print("Workflow demonstration stopped at Step 1")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_workflow()
