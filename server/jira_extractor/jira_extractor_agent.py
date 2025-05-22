import os
from openai import AzureOpenAI
import re
import ast
from jira import JIRA
import os
from dotenv import load_dotenv
import json

load_dotenv()

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
    
    def get_jira_issues(self, query: dict) -> dict:
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
        print(f"\ntopic: {topic}")
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

    def extract_json_from_response(self, response_text):
        """
        Extracts and parses JSON data from a response text.
        First tries to find JSON pattern, then applies multiple parsing approaches.

        Args:
            response_text (str): A string containing JSON data somewhere within it

        Returns:
            dict: The parsed JSON data as a Python dictionary
        """
        try:
            # Step 1: Use regex to find JSON pattern in response (original approach)
            json_match = re.search(r'{.*}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No valid JSON found in the response.")

            json_str = json_match.group()

            # Step 2: Try direct parsing
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

            # Step 3: Handle single quotes vs double quotes issue
            normalized = json_str.replace("\\'", "___ESCAPED_SINGLE_QUOTE___")
            normalized = re.sub(r"(?<![\\])\'", "\"", normalized)
            normalized = normalized.replace("___ESCAPED_SINGLE_QUOTE___", "\\'")

            try:
                return json.loads(normalized)
            except json.JSONDecodeError:
                pass

            # Step 4: More aggressive cleaning for malformed JSON
            cleaned = json_str.strip()
            cleaned = re.sub(r"(?<![\\])\'", "\"", cleaned)
            cleaned = re.sub(r'(?<!")(\w+)(?=":)', r'"\1"', cleaned)
            cleaned = re.sub(r',\s*}', '}', cleaned)
            cleaned = re.sub(r',\s*]', ']', cleaned)

            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass

            # Step 5: Last resort - use ast.literal_eval
            try:
                return ast.literal_eval(json_str)
            except:
                raise ValueError(f"Failed to parse JSON after multiple attempts: {json_str[:50]}...")

        except Exception as e:
            raise ValueError(f"Error processing JSON: {str(e)}")


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
    print('\n\nstart extracting topics...')
    topics_response = agent.invoke(topics_prompt, "You are a helpful assistant that extracts topics from a description.")
    topics_list = agent.extract_json_from_response(topics_response)["topics"]
    print(topics_list)

    issues = {}
    print('\n\nstart extracting issues from Jira...')
    for topic in topics_list:
        print(f'start extracting issues for topic: {topic}')
        issues[topic] = agent.get_jira_issues({"topic": topic})
    print(f'\n\nissues: {issues}')

    print('\n\nstart filtering issues...')
    filter_issues_prompt = agent.filter_issues_prompt(issues, topics_list)
    filter_issues_response = agent.invoke(filter_issues_prompt, "You are a helpful assistant that filters issues based on a topic.")
    filtered_issues = agent.extract_json_from_response(filter_issues_response)["issues"]
    print(f'\n\nfiltered issues: {filtered_issues}')

    return filtered_issues

if __name__ == "__main__":
    agent = JiraExtractorAgent()

    tasks_description_json = {
        "tasks_description": "backend development, user authentication, signup page, database design, api integration, database schema, api endpoints, kubernetes, CI/CD, error logging, monitoring, unit tests, performance optimization, frontend state management, automated backup, documentation, data validation, notification system, mobile-responsive layouts, load balancing, search functionality, user onboarding",
        "language": "python, REACT, CSS, HTML"
    }

    response = main(tasks_description_json)
    print(response)

