#!/usr/bin/env python3
"""
GitHub Agent Runner

This script provides a simplified interface to run the GitHub repository clone agent.
"""

import os
import sys
import logging
from github_agent import create_github_agents, GitHubCloneAgent

def main():
    """Main function to run the GitHub agent"""
    print("=" * 60)
    print("GitHub Repository Clone and Analysis Agent")
    print("=" * 60)
    print("This agent can:")
    print("1. Clone GitHub repositories")
    print("2. Analyze repository structure and content")
    print("3. Answer questions about the code")
    print("-" * 60)
    print("Example commands:")
    print("- 'clone microsoft/autogen'")
    print("- 'analyze the repository structure'")
    print("- 'find all Python files'")
    print("- 'what does this repository do?'")
    print("-" * 60)
    
    # Hard-code Azure OpenAI settings
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://ai-adielashrov6571ai547362566329.services.ai.azure.com"
    os.environ["AZURE_OPENAI_API_KEY"] = "your-actual-api-key"  # Replace with your actual key
    os.environ["DEPLOYMENT_NAME"] = "Phi-4-mini-instruct"

    # Check if a command was provided as an argument
    initial_message = None
    if len(sys.argv) > 1:
        initial_message = " ".join(sys.argv[1:])
        print(f"Starting with request: '{initial_message}'")
    else:
        print("Starting GitHub agent in interactive mode...")
    
    print("-" * 60)
    
    # Run the GitHub agent
    try:
        # Configure standard AutoGen with Azure OpenAI
        endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
        api_key = os.environ["AZURE_OPENAI_API_KEY"]
        deployment_name = os.environ["DEPLOYMENT_NAME"]
        
        # Create the Azure OpenAI config
        config_list = [
            {
                "model": deployment_name,
                "api_type": "azure",
                "api_key": api_key,
                "api_version": "2023-07-01-preview",  # Update this to your Azure OpenAI API version
                "api_base": endpoint,
                "deployment_name": deployment_name
            }
        ]
        
        # Configure AutoGen with the Azure OpenAI config
        llm_config = {
            "config_list": config_list,
            "cache_seed": 42  # Optional: for reproducibility
        }
        
        # Create agents with the LLM configuration
        agents = create_github_agents(use_llm=True, llm_config=llm_config)
        
        # Initialize a group chat with the agents
        import autogen
        
        groupchat = autogen.GroupChat(
            agents=[agents["assistant"], agents["github_agent"], agents["user_proxy"]],
            messages=[],
            max_round=10
        )
        
        # Create a manager for the group chat with our Azure OpenAI LLM config
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
        
        # Start the conversation as the user proxy
        if initial_message:
            agents["user_proxy"].initiate_chat(
                manager,
                message=initial_message
            )
        else:
            agents["user_proxy"].initiate_chat(
                manager,
                message="I need help with GitHub repository operations. Can you assist me?"
            )
    except KeyboardInterrupt:
        print("\nGitHub agent stopped by user.")
    except Exception as e:
        print(f"\nError running GitHub agent: {str(e)}")
        import traceback
        traceback.print_exc()  # Print the full traceback for better debugging
    
    print("\nThank you for using the GitHub Repository Agent!")

if __name__ == "__main__":
    main()