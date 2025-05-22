# server/api/index.py
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

from jira_extractor.agents_workflow import main_agents_workflow
import mcpServer_managerPrompt

app = Flask(__name__)
CORS(app)  # allow all origins during dev


# ---------- helpers ---------------------------------------------------------
def parse_maybe_json(value):
    """Return dict if value is JSON or dict, otherwise None."""
    if isinstance(value, dict):
        print('\n\nparsed dict value:')
        print(value)
        return value
    if isinstance(value, str):
        try:
            print('\n\nparsed str value:')
            print(value)
            return json.loads(value)
        except json.JSONDecodeError:
            print('\n\nerror value:')
            print(value)
            return None
    print('\n\nerror value:')
    print(value)
    return None


def is_final(answer_dict):
    return isinstance(answer_dict, dict) and "managerPrompt" in answer_dict


# ---------- route -----------------------------------------------------------
@app.route("/user-message", methods=["POST"])
def user_message():
    prompt = request.json.get("message")
    print("Received user message:", prompt)

    if not isinstance(prompt, str) or not prompt.strip():
        return jsonify({"error": "message must be a non‑empty string"}), 400

    # --- one pass through your main agent ----------------------------------
    raw_reply = main_agents_workflow(prompt) 
    print('\n\nraw reply:')
    print(raw_reply)
    # may be str or dict
    reply_dict = parse_maybe_json(raw_reply)

    return jsonify(reply_dict)

    # --- not final → fall back to generic generator -------------------------
    try:
        final_json = mcpServer_managerPrompt.generate_manager_prompt_conversation(
            prompt  # single prompt, one‑shot
        )
        return jsonify(final_json)
    except Exception as e:
        # last resort: return the raw text plus error info
        return jsonify({"assistant": raw_reply, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
