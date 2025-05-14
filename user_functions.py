from jira import JIRA
import os
from dotenv import load_dotenv
import shutil  # Added missing import for shutil module
import subprocess

def get_jira_issues(query: dict) -> dict:
    """
    Return {issue_key: summary} for issues whose text contains the given topic.
    """
    jira = JIRA(
        server="https://generated-interview-task.atlassian.net",    # e.g. "https://acme.atlassian.net"
        basic_auth=(                 # ► store secrets in env‑vars or Config
            os.getenv("JIRA_EMAIL"),  # or Config.JIRA_EMAIL
            os.getenv("JIRA_API_TOKEN"),
        ),
    )

    topic = query.get("topic")
    if not topic:
        return {}

    # Build a proper JQL clause; quote the phrase so spaces are allowed
    jql = f'text ~ "{topic}" ORDER BY created DESC'
    issues = jira.search_issues(jql)

    # jql = "SCRUM-1"
    # issues = jira.issue(jql)

    

    print('issues:')
    print(issues)

    return {i.key: i.fields.summary for i in issues}

def clone_github_repo(repo_url: str, clone_dir: str = "./cloned_repo"):
    if not shutil.which("git"):
        raise EnvironmentError("Git is not installed or not in PATH.")

    if os.path.exists(clone_dir):
        raise FileExistsError(f"Directory '{clone_dir}' already exists.")
    
    try:
        subprocess.run(["git", "clone", repo_url, clone_dir], check=True)
        print(f"Repository cloned to {clone_dir}")
    except subprocess.CalledProcessError as e:
        print("Failed to clone repository:", e)


if __name__ == "__main__":
    # print(get_jira_issues({"topic": "signup"}))
    print(clone_github_repo("https://github.com/adielashrov/trust-ai-roma-for-llm", "./trust-ai-roma-for-llm"))
