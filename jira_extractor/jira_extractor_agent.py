import os
from openai import AzureOpenAI
from user_functions import get_jira_issues
from utils import extract_json_from_response

class JiraExtractorAgent:
    def __init__(self):
        self.endpoint = "https://ai-dentzbar2802ai654595622363.openai.azure.com/"
        self.model_name = "gpt-4.1"
        self.deployment = "gpt-4.1"
        self.api_version = "2024-12-01-preview"
        
        self.subscription_key = os.getenv("AZURE_OPENAI_API_KEY_JIRA_EXT")
        
        self.client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            api_key=self.subscription_key,
        )

    def topics_prompt(self, tasks_description_json: dict) -> str:
        prompt = f"""
        your task is to extract the main topics from the tasks description, return them in a list of strings.
        these topics will be used for issues search in jira, so make sure they are clear and specific.
        each topic should be a single key word, give as many key words as you can.
        The description is: {tasks_description_json}

        return your response in json format, like this:
        {{
            "topics": ["topic1", "topic2", "topic3"]
        }}
        """
        return prompt
    
    def filter_issues_prompt(self, issues_list: list, topics_list: list) -> str:
        prompt = f"""
        your task is to filter the issues list based on the topics list.

        the topics list is: 
        {topics_list}

        the issues list is: 
        {issues_list}
        
        return up to 10 issues that are most relevant to the topics.

        return your response in json format, like this:
        {{
            "issues": ["issue1", "issue2", "issue3"]
        }}
        """
        return prompt

    def invoke(self, prompt: str, system_prompt: str) -> str:
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_completion_tokens=800,
            temperature=1.0,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            model=self.deployment
        )
        
        return response.choices[0].message.content

def main(tasks_description_json: dict) -> dict:
    agent = JiraExtractorAgent()
    topics_prompt = agent.topics_prompt(tasks_description_json)
    topics_response = agent.invoke(topics_prompt, "You are a helpful assistant that extracts topics from a description.")
    topics_list = extract_json_from_response(topics_response)["topics"]
    print(topics_list)

    issues = {}

    for topic in topics_list:
        issues[topic] = get_jira_issues({"topic": topic})

    filter_issues_prompt = agent.filter_issues_prompt(issues, topics_list)
    filter_issues_response = agent.invoke(filter_issues_prompt, "You are a helpful assistant that filters issues based on a topic.")
    filtered_issues = extract_json_from_response(filter_issues_response)["issues"]

    return filtered_issues

if __name__ == "__main__":
    agent = JiraExtractorAgent()

    tasks_description_json = {
        "tasks_description": "backend development, user authentication, signup page, database design, api integration, database schema, api endpoints, kubernetes, CI/CD, error logging, monitoring, unit tests, performance optimization, frontend state management, automated backup, documentation, data validation, notification system, mobile-responsive layouts, load balancing, search functionality, user onboarding",
        "language": "python, REACT, CSS, HTML"
    }

    response = main(tasks_description_json)
    print(response)

