from flask import Flask,request,jsonify
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/user-message', methods=['POST'])
def user_message():
    user_message = request.json.get('message')
    print(f"Received user message: {user_message}")
    return jsonify({'message': "answer"})

    # # Send user message to prompt manager (replace with your logic)
    # prompt_manager_answer = send_to_prompt_manager(user_message)

    # # Check if it's the final answer from prompt manager
    # if is_final_answer(prompt_manager_answer):
    #     # Send final answer to GitAgentManager and JiraAgentManager
    #     git_answer = send_to_git_agent_manager(prompt_manager_answer)
    #     jira_answer = send_to_jira_agent_manager(prompt_manager_answer)

    #     # Send both answers as prompt to task generator
    #     task_generator_answer = send_to_task_generator(git_answer, jira_answer)

    #     return jsonify({'prompt_manager_answer': prompt_manager_answer, 'task_generator_answer': task_generator_answer})
    # else:
    #     return jsonify({'prompt_manager_answer': prompt_manager_answer})

def send_to_prompt_manager(message):
    # Implement logic to send message to prompt manager and receive answer
    # Replace with actual implementation
    return "Prompt manager response"

def is_final_answer(answer):
    # Implement logic to determine if the answer is final
    # Replace with actual implementation
    return True  # Example: Always consider it final for now

def send_to_git_agent_manager(answer):
    # Implement logic to send answer to GitAgentManager and receive response
    # Replace with actual implementation
    return "Git agent response"

def send_to_jira_agent_manager(answer):
    # Implement logic to send answer to JiraAgentManager and receive response
    # Replace with actual implementation
    return "Jira agent response"

def send_to_task_generator(git_answer, jira_answer):
    # Implement logic to send answers to task generator and receive response
    # Replace with actual implementation
    return "Task generator response"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Runs on localhost:5000
