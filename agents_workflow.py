from jira_extractor.jira_extractor_agent import main as jira_extractor_agent

def main_agents_workflow(tasks_description_json):
    data_json = {}

    # 1. Jira Extractor Agent
    jira_response_json = jira_extractor_agent(tasks_description_json)
    data_json["jira_response_json"] = jira_response_json

    # 2. Github Repo Agent
    github_response_json = github_repo_agent(tasks_description_json)
    data_json["github_response_json"] = github_response_json

    # 2. Code Generation Agent
    generated_task_response_json = task_generator_agent(data_json)

    return generated_task_response_json

if __name__ == "__main__":
    tasks_description_json = {
        "tasks_description": "backend development, user authentication, signup page, database design, api integration",
        "language": "python, REACT, CSS, HTML"
    }

    generated_task_response_json = main_agents_workflow(tasks_description_json)
    print(generated_task_response_json)
