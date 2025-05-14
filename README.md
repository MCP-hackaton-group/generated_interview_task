# Technical Interview Task Generator

This project automates the generation of technical interview assignments by integrating multiple AI agents to create customized, realistic coding tasks based on job requirements.

## 🌟 Overview

The Technical Interview Task Generator creates personalized coding assignments by:

1. **Extracting relevant tasks** from a Jira-like database
2. **Processing requirements** through a manager prompt agent
3. **Generating** a complete technical interview assignment

The workflow connects these components into a seamless pipeline, taking simple input parameters (task description and programming languages) and outputting a structured, comprehensive interview assignment.

## 🚀 Components

### 1. Jira Extractor Agent
- Extracts relevant tasks and technical requirements
- Analyzes skills needed for the position
- Provides structured data about technical needs

### 2. Manager Prompt Agent
- Transforms Jira data into clear job requirements
- Creates structured format for expected skills and focus areas
- Defines assignment parameters (difficulty, estimated time, etc.)

### 3. Task Generator Agent
- Builds complete interview assignments based on requirements
- Creates task descriptions, evaluation criteria, and more
- Formats everything into a comprehensive assignment document

## 📋 API Endpoints

The system exposes a REST API endpoint:

- **POST /user-message**
  - Input: JSON object with `task_description` and `language` fields
  - Output: Complete structured interview assignment

Example request body:
```json
{
  "message": {
    "task_description": "backend development, user authentication, database design, API endpoints",
    "language": "Python, FastAPI, PostgreSQL"
  }
}
```

## 🛠️ Getting Started

### Prerequisites
- Python 3.8+
- Required Python packages (see requirements.txt)
- Access to OpenAI API (for the AI agents)

### Setup and Run
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server using the provided script:
   ```bash
   run_server.bat
   ```
   This will start the API server at `http://localhost:5001`.

4. The final assignment files will be saved in the `results` directory.

### Using the API

You can use the API in several ways:

1. **Using the test client**:
   ```bash
   python test_api.py
   ```
   This will prompt for task description and languages or accept them as command-line arguments.

2. **Direct API call** with curl:
   ```bash
   curl -X POST http://localhost:5001/user-message -H "Content-Type: application/json" -d "{\"message\":{\"task_description\":\"backend development, authentication\",\"language\":\"Python, FastAPI\"}}"
   ```

3. **From a web client** - send a POST request to `http://localhost:5001/user-message` with this JSON structure:
   ```json
   {
     "message": {
       "task_description": "backend development, user authentication, database design",
       "language": "Python, FastAPI, PostgreSQL"
     }
   }
   ```

### Testing Tools

Several testing utilities are provided:

1. **demo_workflow.py**: Shows a step-by-step visualization of the entire process
   ```bash
   python demo_workflow.py
   ```
   This tool provides a detailed interactive demonstration of each step in the workflow.

2. **test_api.py**: Tests the API endpoint with custom inputs
   ```bash
   python test_api.py "backend development, user authentication" "Python, FastAPI"
   ```
   Great for quickly testing if the API is working correctly.

3. **test_workflow.py**: Validates the integration between components
   ```bash
   python test_workflow.py
   ```
   Runs multiple test cases to ensure the workflow is functioning properly.

### Where to Find Generated Assignments

All generated files are saved in the `results` directory with timestamped filenames:

- `results/api_result_TIMESTAMP.json` - API call results
- `results/assignment_TIMESTAMP.json` - Demo workflow results
- `results/test_*_TIMESTAMP.json` - Test workflow results

## 📊 Output Format

The system generates a structured JSON output containing:

- Title and description of the assignment
- Required and bonus tasks
- Evaluation criteria
- Time estimates
- Setup instructions
- Technical requirements

Example output structure:
```json
{
  "title": "User Authentication API Development Assignment",
  "shortDescription": "Build a secure API with user authentication using Python and FastAPI",
  "requiredTasks": [
    {
      "id": "task-1",
      "title": "Implement user registration endpoint",
      "description": "Create an API endpoint for user registration with proper validation"
    },
    ...
  ],
  "bonusTasks": [...],
  "evaluationCriteria": [...],
  "setupInstructions": "...",
  "technicalRequirements": [...],
  "timeEstimate": "3-4 hours",
  "submissionGuidelines": "..."
}
```

## 📄 Files

- `agents_workflow.py`: Main integration file connecting all components
- `server/api/index.py`: API server implementation
- `demo_workflow.py`: Interactive demonstration of the workflow
- `test_api.py`: API testing client
- `test_workflow.py`: Workflow integration tests
- `run_server.bat`: Server startup script

## 🔄 Workflow Diagram

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  Jira Extractor │──────▶ Manager Prompt  │──────▶ Task Generator  │
│     Agent       │      │     Agent       │      │     Agent       │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
       │                        │                        │
       │                        │                        │
       ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                     Complete API Response                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🔍 Troubleshooting

If you encounter issues:

1. Check the console logs for detailed error messages
2. Ensure all required dependencies are installed
3. Verify API access keys are set correctly in environment variables
4. For specific component errors, check the respective logs in the results directory

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
