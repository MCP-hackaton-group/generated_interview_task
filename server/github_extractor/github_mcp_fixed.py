#!/usr/bin/env python3
import asyncio
import logging
import json
import argparse
import traceback
from mcp import ClientSession
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from contextlib import AsyncExitStack

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("github_mcp")

class GitHubMCPClient:
    def __init__(self, container_name="GitHub-MCP-Server", timeout=60.0):  # Increased timeout to 60 seconds
        self.container_name = container_name
        self.timeout = timeout
        self.session = None
        self.available_tools = []
        self.exit_stack = AsyncExitStack()
    
    async def connect(self):
        """Establish connection to the GitHub MCP server"""
        logger.info(f"Connecting to GitHub MCP server in container '{self.container_name}'")
        
        # Add specific command to run the MCP server in the container
        server_params = StdioServerParameters(
            command="docker",
            args=["exec", "-i", self.container_name, "./github-mcp-server", "stdio"]
        )
        
        try:
            # Use AsyncExitStack to manage the async context managers
            logger.debug("Creating transport...")
            transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.read_stream, self.write_stream = transport
            logger.debug("Transport created, setting up ClientSession...")
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.read_stream, self.write_stream))
            
            logger.debug("Initializing session...")
            await asyncio.wait_for(self.session.initialize(), timeout=self.timeout)
            logger.info("Session initialized successfully")
            
            # Get available tools
            tools_response = await self.session.list_tools()
            self.available_tools = tools_response.tools if hasattr(tools_response, 'tools') else []
            tool_names = [getattr(tool, 'name', str(tool)) for tool in self.available_tools]
            logger.info(f"Available tools: {tool_names}")
            return True
        except asyncio.TimeoutError:
            logger.error(f"Session initialization timed out after {self.timeout} seconds")
            return False
        except Exception as e:
            logger.error(f"Error during session initialization: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def search_repositories(self, query, sort="stars", order="desc", per_page=30, page=1):
        """Search for GitHub repositories"""
        if not self.session:
            raise RuntimeError("Session not initialized. Call connect() first.")
        
        logger.info(f"Searching repositories with query: {query}")
        result = await self.session.call_tool(
            "search_repositories",
            {
                "query": query,
                "sort": sort,
                "order": order,
                "per_page": per_page,
                "page": page
            }
        )
        return result
    
    async def search_code(self, query, filename=None, extension=None, repo=None, owner=None, page=1, per_page=30):
        """Search for code in GitHub repositories"""
        if not self.session:
            raise RuntimeError("Session not initialized. Call connect() first.")
        
        params = {
            "query": query,
            "per_page": per_page,
            "page": page
        }
        
        # Add optional parameters if provided
        if filename:
            params["filename"] = filename
        
        if extension:
            params["extension"] = extension
            
        if repo and owner:
            params["repo"] = f"{owner}/{repo}"
        
        logger.info(f"Searching code with query: {query}")
        result = await self.session.call_tool("search_code", params)
        return result
        
    async def get_repository(self, owner, repo):
        """Get details for a specific repository using search_repositories"""
        if not self.session:
            raise RuntimeError("Session not initialized. Call connect() first.")
        
        logger.info(f"Getting repository information for: {owner}/{repo}")
        result = await self.session.call_tool(
            "search_repositories", 
            {"query": f"repo:{owner}/{repo}"}
        )
        return result
    
    async def list_issues(self, owner, repo, state="open", sort="created", direction="desc", per_page=30, page=1):
        """List issues for a repository"""
        if not self.session:
            raise RuntimeError("Session not initialized. Call connect() first.")
        
        logger.info(f"Listing issues for repository: {owner}/{repo}")
        result = await self.session.call_tool(
            "list_issues",
            {
                "owner": owner,
                "repo": repo,
                "state": state,
                "sort": sort,
                "direction": direction,
                "per_page": per_page,
                "page": page
            }
        )
        return result
    
    async def create_issue(self, owner, repo, title, body="", labels=None):
        """Create a new issue in a repository"""
        if not self.session:
            raise RuntimeError("Session not initialized. Call connect() first.")
        
        params = {
            "owner": owner,
            "repo": repo,
            "title": title,
            "body": body
        }
        
        if labels:
            params["labels"] = labels
            
        logger.info(f"Creating issue in repository: {owner}/{repo}")
        result = await self.session.call_tool("create_issue", params)
        return result
    
    async def list_pull_requests(self, owner, repo, state="open", sort="created", direction="desc", per_page=30, page=1):
        """List pull requests for a repository"""
        if not self.session:
            raise RuntimeError("Session not initialized. Call connect() first.")
        
        logger.info(f"Listing pull requests for repository: {owner}/{repo}")
        result = await self.session.call_tool(
            "list_pull_requests",
            {
                "owner": owner,
                "repo": repo,
                "state": state,
                "sort": sort,
                "direction": direction,
                "per_page": per_page,
                "page": page
            }
        )
        return result
    
    async def get_file_contents(self, owner, repo, path, ref=None):
        """Get the contents of a file in a GitHub repository"""
        if not self.session:
            raise RuntimeError("Session not initialized. Call connect() first.")
        
        params = {
            "owner": owner,
            "repo": repo,
            "path": path
        }
        
        if ref:
            params["ref"] = ref
            
        logger.info(f"Getting file contents: {owner}/{repo}/{path}")
        result = await self.session.call_tool("get_file_contents", params)
        return result
        
    async def get_user(self, username):
        """Get details for a GitHub user"""
        if not self.session:
            raise RuntimeError("Session not initialized. Call connect() first.")
        
        logger.info(f"Getting user information for: {username}")
        result = await self.session.call_tool("get_user", {"username": username})
        return result
    
    async def close(self):
        """Close the session"""
        if self.exit_stack:
            logger.info("Closing session")
            await self.exit_stack.aclose()
            self.session = None


class JSONEncoderWithCallToolResult(json.JSONEncoder):
    def default(self, obj):
        # Convert any object to a serializable format
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

def serialize_result(result):
    """Convert a result object to a JSON-serializable format"""
    if hasattr(result, 'result'):
        # If the object has a 'result' attribute, use that
        result_data = result.result
    elif hasattr(result, '__dict__'):
        # If it's an object with a __dict__, convert to dict
        result_data = result.__dict__
    else:
        # Otherwise just return as is and let the JSONEncoderWithCallToolResult handle it
        result_data = result
    return result_data


async def main():
    """Main entry point for the GitHub MCP client"""
    parser = argparse.ArgumentParser(description="GitHub MCP Client")
    parser.add_argument("--container", default="GitHub-MCP-Server", help="Docker container name")
    parser.add_argument("--timeout", type=float, default=30.0, help="Connection timeout in seconds")
    parser.add_argument("--search", help="Search for repositories with the given query")
    parser.add_argument("--repo", help="Repository in format owner/repo for operations")
    parser.add_argument("--user", help="GitHub username for user operations")
    parser.add_argument("--list-issues", action="store_true", help="List issues for the specified repository")
    parser.add_argument("--list-pulls", action="store_true", help="List pull requests for the specified repository")
    parser.add_argument("--search-code", help="Search for code with the given query")
    parser.add_argument("--filename", help="Filter code search by filename")
    parser.add_argument("--extension", help="Filter code search by file extension")
    parser.add_argument("--path", help="Get contents of a file at the specified path in the repository")
    parser.add_argument("--ref", help="The name of the commit/branch/tag for file contents")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging based on verbose flag
    if not args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    
    client = GitHubMCPClient(container_name=args.container, timeout=args.timeout)
    
    try:
        connected = await client.connect()
        if not connected:
            print("Failed to connect to the GitHub MCP server. Check logs for details.")
            return 1
        
        # Handle repository search
        if args.search:
            result = await client.search_repositories(args.search)
            result_data = serialize_result(result)
            print(json.dumps(result_data, indent=2, cls=JSONEncoderWithCallToolResult))
            
        # Handle code search
        if args.search_code:
            # Check if we need to scope the search to a specific repo
            owner = None
            repo = None
            if args.repo:
                try:
                    owner, repo = args.repo.split("/")
                except ValueError:
                    print("Repository must be in format 'owner/repo'")
                    return 1
                
            result = await client.search_code(
                query=args.search_code,
                filename=args.filename,
                extension=args.extension,
                owner=owner,
                repo=repo
            )
            result_data = serialize_result(result)
            print(json.dumps(result_data, indent=2, cls=JSONEncoderWithCallToolResult))
        
        # Handle file content retrieval
        if args.repo and args.path:
            try:
                owner, repo = args.repo.split("/")
            except ValueError:
                print("Repository must be in format 'owner/repo'")
                return 1
            
            file_contents = await client.get_file_contents(
                owner=owner,
                repo=repo,
                path=args.path,
                ref=args.ref
            )
            result_data = serialize_result(file_contents)
            print(json.dumps(result_data, indent=2, cls=JSONEncoderWithCallToolResult))
        
        # Handle repository operations
        if args.repo:
            try:
                owner, repo = args.repo.split("/")
            except ValueError:
                print("Repository must be in format 'owner/repo'")
                return 1
            
            if args.list_issues:
                issues = await client.list_issues(owner, repo)
                result_data = serialize_result(issues)
                print(json.dumps(result_data, indent=2, cls=JSONEncoderWithCallToolResult))
            
            if args.list_pulls:
                pulls = await client.list_pull_requests(owner, repo)
                result_data = serialize_result(pulls)
                print(json.dumps(result_data, indent=2, cls=JSONEncoderWithCallToolResult))
            
            # If no specific operation is requested, get repository details
            if not (args.list_issues or args.list_pulls or args.path or args.search_code):
                repo_details = await client.get_repository(owner, repo)
                result_data = serialize_result(repo_details)
                print(json.dumps(result_data, indent=2, cls=JSONEncoderWithCallToolResult))
        
        # Handle user operations
        if args.user:
            user_details = await client.get_user(args.user)
            result_data = serialize_result(user_details)
            print(json.dumps(result_data, indent=2, cls=JSONEncoderWithCallToolResult))
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 1
    finally:
        await client.close()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
