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


app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/prompt", methods=["POST"])
def prompt():
    data = request.get_json(force=True, silent=True) or {}
    user_msg = data.get("message", "").strip()

    if not user_msg:
        return jsonify({"error": "Missing 'message' in body"}), 400

    try:
        response = client.chat.completions.create(
            model="PromptAgent",
            messages=[{"role": "user", "content": user_msg}],
            max_completion_tokens=1024,
        )
        assistant_msg = response.choices[0].message.content
        return jsonify({"answer": assistant_msg}), 200

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

@app.route("/generate-assignment", methods=["POST"])
def generate_assignment():
    data = request.get_json(force=True, silent=True) or {}
    
    jira_tasks = data.get("jiraTasks")
    prompt_data = data.get("prompt")
    template_repo = data.get("templateRepo")
    
    if not jira_tasks or not prompt_data or not template_repo:
        missing_fields = []
        if not jira_tasks: missing_fields.append("jiraTasks")
        if not prompt_data: missing_fields.append("prompt")
        if not template_repo: missing_fields.append("templateRepo")
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    try:
        system_prompt = """
        You are an assistant designed to generate technical home assignments for developer candidates based on three input sources:
        
        1. Jira Tasks JSON: Analyze the list of tasks and understand the technical stack and job expectations.
        2. Prompt JSON: Understand the hiring manager's goals, role type, seniority level, and preferred focus (e.g., frontend, backend, DevOps).
        3. Template Repository JSON: Extract the structure, file patterns, and placeholder logic to base the assignment on.
        
        Using these three inputs, create a well-structured JSON homeAssignment with the following:
        - Title and short description
        - List of required tasks
        - Technologies and tools to be used
        - Evaluation criteria
        - Clear instructions on what to submit
        
        The assignment should be:
        - Aligned with the role and difficulty level in the prompt
        - Inspired by real Jira tasks
        - Consistent with the template structure
        
        Respond only with valid JSON formatted as a homeAssignment object.
        """
        
        user_message = f"""
        Generate a technical home assignment based on the following inputs:
        
        JIRA TASKS:
        {json.dumps(jira_tasks, indent=2)}
        
        PROMPT:
        {json.dumps(prompt_data, indent=2)}
        
        TEMPLATE REPOSITORY:
        {json.dumps(template_repo, indent=2)}
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
        
        assignment_json = response.choices[0].message.content
        
        assignment_data = json.loads(assignment_json)
        
        return jsonify(assignment_data), 200

    except json.JSONDecodeError:
        return jsonify({"error": "Failed to generate valid JSON response"}), 500
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
