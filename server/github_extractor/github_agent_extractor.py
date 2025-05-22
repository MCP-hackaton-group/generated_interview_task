from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, END
from langchain.agents import Tool, AgentExecutor, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_toolkits import create_react_agent
from dotenv import load_dotenv

load_dotenv()

# 1. Initialize the MCP client for GitHub MCP
mcp_client = MultiServerMCPClient({
    "github": {
        "url": "http://localhost:8080/mcp",
        "transport": "streamable_http",
    }
})

# 2. Load tools from GitHub MCP
github_tools = mcp_client.load_tools("github")

# 3. Define a language model (e.g., GPT-4 or GPT-3.5)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 4. Initialize a ReAct agent using the tools and LLM
agent = create_react_agent(llm, github_tools)
executor = AgentExecutor(agent=agent, tools=github_tools, verbose=True)

# 5. LangGraph wrapper
def invoke_agent(state):
    input_text = state['input']
    response = executor.invoke({"input": input_text})
    return {"output": response['output']}

# 6. LangGraph graph
graph = StateGraph()
graph.add_node("agent", invoke_agent)
graph.set_entry_point("agent")
graph.set_finish_point(END)

# 7. Compile and run the graph
app = graph.compile()

if __name__ == "__main__":
    user_input = "List all issues assigned to me in GitHub."
    final_output = app.invoke({"input": user_input})
    print("\nFinal output:", final_output["output"])
