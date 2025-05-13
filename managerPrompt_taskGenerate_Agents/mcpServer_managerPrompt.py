from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from openai import AzureOpenAI

load_dotenv()
azure_openai_key = os.getenv("AZURE_OPENAI_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = "PromptAgent"

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
