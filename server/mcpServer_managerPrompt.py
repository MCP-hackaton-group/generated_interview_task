import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

azure_openai_key = os.getenv("AZURE_OPENAI_KEY_TASK_GEN")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_TASK_GEN")
deployment_name = "PromptAgent"

client = AzureOpenAI(
    api_key=azure_openai_key,
    api_version="2024-12-01-preview",
    azure_endpoint=azure_endpoint
)

# Updated SYSTEM_PROMPT for only one iteration
# ---------- SYSTEM_PROMPT ----------
SYSTEM_PROMPT = """
You are a warm, friendly assistant helping hiring managers create job requirements
for technical take‑home assignments. You receive ONE user prompt only and must
return a single JSON object with this structure:

{
"final": "true",
"managerPrompt": {
  "version": "1.0",
  "generatedOn": "Current date"
},
"role": {
  "title": "Job title",
  "level": "Seniority level",
  "focus": ["area1", "area2"],
  "description": "Detailed role description"
},
"requirements": {
  "skills": {
    "must_have": ["skill1", "skill2", "skill3"],
    "nice_to_have": ["skill4", "skill5"]
  }
},
"assignment_preferences": {
  "difficulty": "Easy/Medium/Hard",
  "estimated_hours": "X‑Y",
  "areas_to_test": ["area1", "area2"]
}
}

If information is missing, invent reasonable defaults. Do NOT ask follow‑up questions.
Return only valid JSON.
"""
# ---------- generator ----------
def generate_manager_prompt_conversation(message: str) -> dict:
    """
    Accept ONE user prompt (string) and return the final JSON.
    """
    if not isinstance(message, str) or not message.strip():
        raise ValueError("message must be a non‑empty string")

    formatted_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": message.strip()}
    ]

    response = client.chat.completions.create(
        model=deployment_name,
        messages=formatted_messages,
        max_completion_tokens=1024,
        temperature=0.7
    )

    content = response.choices[0].message.content.strip()
    if not content:
        raise ValueError("Empty response from OpenAI API")

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("OpenAI did not return valid JSON")
