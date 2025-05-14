from jira import JIRA
import json
import os
from typing import List

def connect_to_jira() -> JIRA:
    """
    Establishes connection to Jira using credentials from environment variables
    """
    jira_server = "https://generated-interview-task.atlassian.net"
    jira_email = os.getenv('JIRA_EMAIL') 
    jira_api_token = os.getenv('JIRA_API_TOKEN')
    
    if not all([jira_server, jira_email, jira_api_token]):
        raise ValueError("Missing required Jira credentials in environment variables")
        
    return JIRA(
        server=jira_server,
        basic_auth=(jira_email, jira_api_token)
    )

def create_jira_issues(titles: List[str], project_key: str) -> List[str]:
    """
    Creates Jira issues from a list of titles
    
    Args:
        titles: List of issue titles to create
        project_key: The Jira project key where issues will be created
        
    Returns:
        List of created issue keys
    """
    jira = connect_to_jira()
    created_issues = []
    
    for title in titles:
        issue_dict = {
            'project': {'key': project_key},
            'summary': title,
            'description': title,  # Using title as description, modify as needed
            'issuetype': {'name': 'Task'}  # Default to Task, modify as needed
        }

        try:
            new_issue = jira.create_issue(fields=issue_dict)
            created_issues.append(new_issue.key)
        except Exception as e:
            print(f"Failed to create issue '{title}': {str(e)}")
            
    return created_issues

def main(titles_list: List[str], project_key: str):
    create_jira_issues(titles_list, project_key)    


if __name__ == "__main__":
    # Generate a comprehensive list of software development tasks
    titles_list = [
        "Implement user authentication system",
        "Design responsive UI for dashboard",
        "Set up CI/CD pipeline with GitHub Actions",
        "Create database schema for user profiles",
        "Develop RESTful API endpoints for product management",
        "Configure Kubernetes cluster for production deployment",
        "Implement error logging and monitoring system",
        "Create unit tests for backend services",
        "Optimize database queries for performance",
        "Implement frontend state management with Redux",
        "Set up automated backup system for databases",
        "Create documentation for API endpoints",
        "Implement data validation middleware",
        "Design and implement notification system",
        "Create mobile-responsive layouts for all pages",
        "Set up load balancing for high availability",
        "Implement search functionality with indexing",
        "Create user onboarding flow and tutorials"
    ]

    project_key = "SCRUM"

    main(titles_list, project_key)






