from jira_extractor.jira_extractor_agent import main as jira_extractor_agent
from managerPrompt_taskGenerate_Agents.mcpServer_taskGenerate import generate_home_assignment
from managerPrompt_taskGenerate_Agents.mcpServer_managerPrompt import generate_manager_prompt_conversation
import json

def main_agents_workflow(tasks_description_json):
    data_json = {}

    # 1. Jira Extractor Agent
    jira_response_json = jira_extractor_agent(tasks_description_json)
    data_json["jira_tasks"] = jira_response_json    # 2. Manager Prompt Agent to process Jira data
    # Extract key information from Jira response for creating a meaningful prompt
    
    # Handle different possible formats of Jira response
    jira_tasks = []
    tech_stack = []
    skills = []
    
    # Extract tasks
    if isinstance(jira_response_json, dict):
        # Try different possible formats
        if "tasks" in jira_response_json and isinstance(jira_response_json["tasks"], list):
            jira_tasks = jira_response_json["tasks"]
        elif "issues" in jira_response_json and isinstance(jira_response_json["issues"], list):
            jira_tasks = [task.get("title", task.get("summary", "")) for task in jira_response_json["issues"] if isinstance(task, dict)]
        
        # Extract tech stack
        if "tech_stack" in jira_response_json:
            tech_stack_data = jira_response_json["tech_stack"]
            if isinstance(tech_stack_data, dict):
                for key, values in tech_stack_data.items():
                    if isinstance(values, list):
                        tech_stack.extend(values)
            elif isinstance(tech_stack_data, list):
                tech_stack = tech_stack_data
        
        # Extract skills
        if "team_skills" in jira_response_json:
            skills_data = jira_response_json["team_skills"]
            if isinstance(skills_data, dict):
                for key, values in skills_data.items():
                    if isinstance(values, list):
                        skills.extend(values)
            elif isinstance(skills_data, list):
                skills = skills_data
        elif "skills" in jira_response_json and isinstance(jira_response_json["skills"], list):
            skills = jira_response_json["skills"]
    
    # Fallback to task description if no tasks found
    if not jira_tasks:
        tasks_desc = tasks_description_json.get('tasks_description', '')
        jira_tasks = [item.strip() for item in tasks_desc.split(',') if item.strip()]
    
    # Create a meaningful first message for the manager prompt
    initial_message = f"I need to create a technical assignment for {tasks_description_json.get('language', 'developers')} " \
                     f"focusing on {tasks_description_json.get('tasks_description', 'coding tasks')}. " \
                     f"Based on the following tasks: {', '.join(jira_tasks[:3] if jira_tasks else ['general development tasks'])}"
                     
    # Create a detailed second message with more specifics about tech and skills
    second_message = f"The technical stack should include {', '.join(tech_stack[:5] if tech_stack else tasks_description_json.get('language', '').split(','))} " \
                    f"and should test skills in {', '.join(skills[:5] if skills else jira_tasks[:3])}"
      # Generate the manager prompt as a structured JSON using our 2-round conversation system
    try:
        manager_prompt_json = generate_manager_prompt_conversation([initial_message, second_message])
        print("Successfully generated manager prompt JSON")
    except Exception as e:
        print(f"Error generating manager prompt: {e}")
        # Fallback: Create a default manager prompt structure
        from datetime import datetime
        
        manager_prompt_json = {
            "managerPrompt": {
                "version": "1.0",
                "generatedOn": datetime.now().strftime("%Y-%m-%d")
            },
            "role": {
                "title": "Developer",
                "level": "Mid-level",
                "focus": [item.strip() for item in tasks_description_json.get('language', '').split(',')[:3]],
                "description": f"Developer role focused on {tasks_description_json.get('tasks_description', 'software development')}"
            },
            "requirements": {
                "skills": {
                    "must_have": [item.strip() for item in tasks_description_json.get('language', '').split(',')],
                    "nice_to_have": []
                }
            },
            "assignment_preferences": {
                "difficulty": "Medium",
                "estimated_hours": "3-4",
                "areas_to_test": [item.strip() for item in tasks_description_json.get('tasks_description', '').split(',')[:3]]
            }
        }
    
    # 3. Github Repo Agent (commented out for now)
    # github_response_json = github_repo_agent(tasks_description_json)
    # data_json["template_repo"] = github_response_json

    # Add the manager prompt JSON to our data JSON
    data_json["prompt_data"] = manager_prompt_json    # Add template repo data if not present
    if "template_repo" not in data_json:
        # Create a simple default template structure based on language
        languages = tasks_description_json.get('language', '').lower()
        
        frontend_tech = []
        if any(tech in languages for tech in ['react', 'angular', 'vue', 'javascript', 'typescript', 'html', 'css']):
            frontend_tech = [tech for tech in languages.split(',') if tech.strip() in ['react', 'angular', 'vue', 'javascript', 'typescript', 'html', 'css']]
        
        backend_tech = []
        if any(tech in languages for tech in ['node', 'express', 'python', 'java', 'ruby', 'php', 'django', 'spring']):
            backend_tech = [tech for tech in languages.split(',') if tech.strip() in ['node', 'express', 'python', 'java', 'ruby', 'php', 'django', 'spring']]
        
        data_json["template_repo"] = {
            "repository": {
                "name": "technical-interview-template",
                "description": f"Template for {manager_prompt_json['role'].get('title', 'Developer')} interview assignment"
            },
            "structure": {
                "frontend": {
                    "technology": ", ".join(frontend_tech) if frontend_tech else "JavaScript",
                    "files": [{"path": "src/App.js", "description": "Main application component"}]
                },
                "backend": {
                    "technology": ", ".join(backend_tech) if backend_tech else "Node.js",
                    "files": [{"path": "server/index.js", "description": "Server entry point"}]
                },
                "documentation": {
                    "files": [{"path": "README.md", "description": "Project documentation"}]
                }
            }
        }
        
    # 4. Code Generation Agent - now using the structured manager prompt
    print("Generating home assignment...")
    generated_task_response_json = generate_home_assignment(data_json)
    print("Home assignment generated successfully!")

    return generated_task_response_json

if __name__ == "__main__":
    tasks_description_json = {
        "tasks_description": "backend development, user authentication, signup page, database design, api integration",
        "language": "python, REACT, CSS, HTML"
    }
    
    print("Starting workflow...")
    print(f"Input: {json.dumps(tasks_description_json, indent=2)}")
    
    generated_task_response_json = main_agents_workflow(tasks_description_json)
    
    print("\n=== WORKFLOW COMPLETED ===")
    print("\nGenerated task assignment:")
    print(json.dumps(generated_task_response_json, indent=2))
