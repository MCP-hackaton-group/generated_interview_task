from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from openai import AzureOpenAI
import json

load_dotenv()
azure_openai_key = os.getenv("AZURE_OPENAI_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = "taskCreator"

client = AzureOpenAI(
    api_key=azure_openai_key,
    api_version="2024-12-01-preview",
    azure_endpoint=azure_endpoint
)


def generate_home_assignment(input_json: dict) -> dict:
    """
    Generate a technical home assignment using Azure OpenAI based on unified JSON input.

    Input JSON structure:
    {
        "jira_tasks": { ... },
        "prompt_data": { ... },
        "template_repo": { ... }
    }

    Returns: dict (homeAssignment JSON)
    """
    jira_tasks = input_json.get("jira_tasks")
    prompt_data = input_json.get("prompt_data")
    template_repo = input_json.get("template_repo")

    if not jira_tasks or not prompt_data or not template_repo:
        raise ValueError("Missing one or more required fields: jira_tasks, prompt_data, template_repo")

    system_prompt = """
    You are an assistant designed to generate technical home assignments for developer candidates based on three input sources:

    1. Jira Tasks JSON
    2. Prompt JSON (role, level, focus, difficulty, etc.)
    3. Template Repository JSON (structure, files)

    Generate a valid JSON homeAssignment with:
    - Title and description
    - List of required tasks
    - Technologies and tools to use
    - Evaluation criteria
    - Clear submission instructions

    Format the output as a valid JSON object only.
    """

    user_message = f"""
    JIRA TASKS:\n{json.dumps(jira_tasks, indent=2)}

    PROMPT:\n{json.dumps(prompt_data, indent=2)}

    TEMPLATE REPOSITORY:\n{json.dumps(template_repo, indent=2)}
    """

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        response_format={"type": "json_object"},
        max_completion_tokens=4096,
    )

    try:
        result = response.choices[0].message.content
        return json.loads(result)
    except json.JSONDecodeError:
        raise ValueError("Failed to parse response as valid JSON.")