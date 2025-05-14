from mcpServer_taskGenerate import generate_home_assignment

input_json = {
    "jira_tasks": {
        "tasks": ["Set up CI pipeline", "Add unit tests for API", "Fix login bug"]
    },
    "prompt_data": {
        "title": "Backend Engineer",
        "level": "Senior",
        "focus": ["API", "DevOps"],
        "difficulty": "Hard"
    },
    "template_repo": {
        "structure": ["src/", "tests/", "Dockerfile", "README.md"]
    }
}

result = generate_home_assignment(input_json)
print(result)
