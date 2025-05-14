from server.mcpServer_managerPrompt import generate_manager_prompt_conversation

result = generate_manager_prompt_conversation([
    "We're hiring a fullstack engineer with Node.js and React experience.",
    "They should be able to work with MongoDB, and experience with Docker is a plus. 6 hours estimated."
])

print(result)
