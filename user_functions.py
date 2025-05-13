from jira import JIRA
import os
from dotenv import load_dotenv
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

if __name__ == "__main__":
    print(get_jira_issues({"topic": "signup"}))
