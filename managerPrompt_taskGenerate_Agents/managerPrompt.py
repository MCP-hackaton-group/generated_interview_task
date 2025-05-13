import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

azure_openai_key = os.getenv("AZURE_OPENAI_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("DEPLOYMENT_NAME", "PromptAgent")

client = AzureOpenAI(
    api_key=azure_openai_key,
    api_version="2024-12-01-preview",
    azure_endpoint=azure_endpoint
)

response = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {"role": "user", "content": "I'm going to Paris, what should I see?"}
    ],
    max_completion_tokens=1024
)

print(response.choices[0].message.content)
