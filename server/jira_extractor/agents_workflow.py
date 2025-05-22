from jira_extractor.jira_extractor_agent import main as jira_extractor_agent
from mcpServer_taskGenerate import generate_home_assignment 
import json
def main_agents_workflow(tasks_description_json):
    data_json = {}

    # 1. Jira Extractor Agent
    print('\n\nstart extracting issues from Jira...')
    jira_response_json = jira_extractor_agent(tasks_description_json)
    data_json["jira_tasks"] = jira_response_json

# 2. Github Repo Agent
    # github_response_json = github_repo_agent(tasks_description_json)
    # Load template repository data from JSON file
    print('\n\nstart loading template repository data...')
    with open("server/jira_extractor/template_repo.json", "r") as file:
        github_response_json = json.loads(file.read())
    data_json["template_repo"] = github_response_json

    data_json["prompt_data"] = tasks_description_json

    # 2. Code Generation Agent
    print('\n\nstart generating home assignment...')
    generated_task_response_json = generate_home_assignment(data_json)
    print('\n\nhome assignment generated successfully:')
    print(generated_task_response_json)

    return generated_task_response_json

if __name__ == "__main__":
    tasks_description_json = {
        "tasks_description": "backend development, user authentication, signup page, database design, api integration",
        "language": "python, REACT, CSS, HTML"
    }

    generated_task_response_json = main_agents_workflow(tasks_description_json)
    print(generated_task_response_json)
