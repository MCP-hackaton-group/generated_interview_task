from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import sys
import os
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import our workflow
from agents_workflow import main_agents_workflow

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/user-message', methods=['POST'])
def user_message():
    # Parse the incoming JSON request
    try:
        user_message = request.json.get('message')
        print(f"Received user message: {user_message}")
        
        # Extract task description and language from user message
        task_description = user_message.get('task_description', '') if isinstance(user_message, dict) else user_message
        language = user_message.get('language', '') if isinstance(user_message, dict) else ''
        
        # Create results directory if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "results"), exist_ok=True)
        
        # Generate timestamp for this request
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create input format for workflow
        input_json = {
            "tasks_description": task_description,
            "language": language
        }
        
        print(f"Starting workflow with input: {json.dumps(input_json)}")
        
        # Save input for reference
        input_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), f"results/api_input_{timestamp}.json")
        with open(input_file, "w") as f:
            json.dump(input_json, f, indent=2)
        
        # Run the workflow with progress logging
        print("Step 1: Starting Jira extraction...")
        result = main_agents_workflow(input_json)
        print("Workflow completed successfully!")
        
        # Save the result
        output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), f"results/api_result_{timestamp}.json")
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Result saved to {output_file}")
        
        # Format the response for the client
        response = {
            'message': "Assignment generated successfully", 
            'result': result,
            'status': 'success',
            'timestamp': timestamp,
            'outputFile': output_file
        }
        
        return jsonify(response)
    except Exception as e:
        print(f"Error processing message: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a more structured error response
        return jsonify({
            'message': f"Error: {str(e)}",
            'status': 'error',
            'error_type': e.__class__.__name__
        }), 500

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
