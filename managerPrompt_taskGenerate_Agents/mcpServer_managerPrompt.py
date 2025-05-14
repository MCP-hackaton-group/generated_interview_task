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

SYSTEM_PROMPT = """
You are a warm, friendly assistant helping hiring managers create job requirements for technical assignments. Your goal is to collect key information in just TWO conversation rounds:

1. Skills required for the role (must-have and nice-to-have)
2. Role description (title, seniority level, focus areas)
3. Assignment details (difficulty, time required, evaluation criteria)

CRITICAL INSTRUCTION: You will ONLY engage in 2 rounds of conversation before generating the final JSON output.

Round 1: After initial message, ask your MOST important questions (maximum 3)
Round 2: After their response, generate the FINAL JSON output with all collected information, making reasonable assumptions for anything missing

CONVERSATIONAL STYLE:
- Be warm, friendly, and conversational - not robotic
- Use a casual, encouraging tone
- Keep responses brief and focused

QUESTION GUIDELINES:
- Ask a STRICT MAXIMUM of 3 questions per response 
- Prioritize the most crucial missing information
- Be specific but gentle in your questions
- Avoid "interrogation" style questioning

EFFICIENCY GUIDELINES:
- Intelligently extract information that's already provided
- Infer reasonable defaults whenever possible
- Remember previous answers - never ask for information already given
- After 2 rounds, you MUST generate the JSON even with incomplete information

Once you have sufficient information, or after the second round of questions, format your response as a valid JSON object with this structure:
{
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
    "estimated_hours": "X-Y",
    "areas_to_test": ["area1", "area2"]
  }
}

Only return JSON when you have sufficient information to create a reasonably complete structure. You can make reasonable assumptions to fill gaps.
"""

def generate_manager_prompt_conversation(messages: list) -> dict:
    """
    Accepts a list of user messages simulating a 2-round conversation.
    Returns a managerPrompt JSON object created by the LLM.
    """
    if not messages or not isinstance(messages, list):
        raise ValueError("Input must be a list of user messages (strings)")

    # Compose messages for the LLM
    formatted_messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    for i, msg in enumerate(messages):
        formatted_messages.append({"role": "user", "content": msg})

        # After 2nd user message, add force-complete instruction
        if i == 1:
            formatted_messages.append({
                "role": "system",
                "content": """
IMPORTANT: This is the second round of the conversation. You MUST now generate the final JSON output 
with all collected information so far, making reasonable assumptions for any missing details.
Do not ask any more questions. Format your response as a valid JSON object only.
"""
            })
            break

    response = client.chat.completions.create(
        model=deployment_name,
        messages=formatted_messages,
        max_completion_tokens=1024,
        temperature=0.7
    )

    try:
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("LLM did not return a valid JSON object.")