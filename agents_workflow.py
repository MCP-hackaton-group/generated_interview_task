from jira_extractor.jira_extractor_agent import main as jira_extractor_agent
from managerPrompt_taskGenerate_Agents.mcpServer_taskGenerate import generate_home_assignment 

def main_agents_workflow(tasks_description_json):
    data_json = {}

    # 1. Jira Extractor Agent
    jira_response_json = jira_extractor_agent(tasks_description_json)
    data_json["jira_tasks"] = jira_response_json

    # 2. Github Repo Agent
    # github_response_json = github_repo_agent(tasks_description_json)
    # data_json["template_repo"] = github_response_json

    data_json["prompt_data"] = tasks_description_json

    # 2. Code Generation Agent
    generated_task_response_json = generate_home_assignment(data_json)

    return generated_task_response_json

if __name__ == "__main__":
    tasks_description_json = {
        "tasks_description": "backend development, user authentication, signup page, database design, api integration",
        "language": "python, REACT, CSS, HTML"
    }

    generated_task_response_json = main_agents_workflow(tasks_description_json)
    print(generated_task_response_json)
