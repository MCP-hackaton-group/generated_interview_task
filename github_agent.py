#!/usr/bin/env python3
"""
GitHub Repository Clone Agent

This script creates an AutoGen agent that can clone GitHub repositories.
It leverages the github_clone.py functionality to handle repository cloning operations.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List, Union
import autogen
from autogen import Agent, AssistantAgent, UserProxyAgent, ConversableAgent

# Import our custom GitHub cloning functionality
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from github_clone import clone_github_repo

# Azure OpenAI settings
endpoint = "https://ai-adielashrov6571ai547362566329.services.ai.azure.com"
model_name = "Phi-4-mini-instruct"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("github_agent.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("github_agent")

# Configuration for the GitHub cloning agent
CONFIG = {
    "clone_base_dir": "./cloned_repos",  # Base directory where repos will be cloned
    "default_branch": "main",            # Default branch if none specified
    "max_attempts": 3,                   # Max attempts to clone a repository
    "timeout": 300,                      # Timeout for clone operations (seconds)
}

class GitHubCloneAgent(UserProxyAgent):
    """
    An AutoGen agent that clones GitHub repositories.
    Extends UserProxyAgent to handle repository cloning operations.
    """
    
    def __init__(self, name: str = "GitHub Clone Agent", **kwargs):
        super().__init__(name=name, **kwargs)
        self.register_function(
            function_map={
                "clone_repository": self.clone_repository,
                "inspect_repository": self.inspect_repository,
                "find_files": self.find_files,
                "read_file_content": self.read_file_content
            }
        )
        self.register_reply(
            trigger=self._is_clone_request,
            reply_func=self.handle_clone_request
        )
        self.register_reply(
            trigger=self._is_inspect_request,
            reply_func=self.handle_inspect_request
        )
        
        # Track the most recently cloned repository
        self.current_repository = None
        
        logger.info(f"Initialized {name} with base directory: {CONFIG['clone_base_dir']}")
        
        # Create base directory if it doesn't exist
        os.makedirs(CONFIG["clone_base_dir"], exist_ok=True)
    
    def _is_clone_request(self, message: Dict[str, Any]) -> bool:
        """
        Check if a message is requesting to clone a repository
        
        Args:
            message: The message to check
            
        Returns:
            True if this is a clone request, False otherwise
        """
        if not isinstance(message, dict) or "content" not in message:
            return False
            
        content = message.get("content", "").lower()
        return ("clone" in content and 
                ("github" in content or "repository" in content or "repo" in content))
    
    def _is_inspect_request(self, message: Dict[str, Any]) -> bool:
        """
        Check if a message is requesting to inspect a repository
        
        Args:
            message: The message to check
            
        Returns:
            True if this is an inspect request, False otherwise
        """
        if not isinstance(message, dict) or "content" not in message:
            return False
            
        content = message.get("content", "").lower()
        inspection_keywords = ["inspect", "analyze", "examine", "check", "look at", "explore", 
                              "structure", "file", "search", "find", "readme", "what's in"]
        
        # If we have a current repository and any inspection-related keyword is present
        if self.current_repository:
            return any(keyword in content for keyword in inspection_keywords)
        
        return False
    
    def _extract_repo_info(self, content: str) -> Dict[str, str]:
        """
        Extract repository information from a message
        
        Args:
            content: The message content
            
        Returns:
            Dictionary containing repo_url, clone_dir, and branch
        """
        words = content.split()
        info = {
            "repo_url": None,
            "clone_dir": None,
            "branch": None
        }
        
        # Look for GitHub URLs or username/repo patterns
        for word in words:
            if "github.com" in word or ("/" in word and not word.startswith(("-", ".", "/"))):
                info["repo_url"] = word.strip(".,;:\"'")
                break
        
        # Look for directory specification
        directory_markers = ["to directory", "to folder", "to dir", "in directory", "in dir"]
        for marker in directory_markers:
            if marker in content:
                parts = content.split(marker)
                if len(parts) > 1:
                    dir_parts = parts[1].split()
                    if dir_parts:
                        info["clone_dir"] = dir_parts[0].strip(".,;:\"'")
                        break
        
        # Look for branch specification
        branch_markers = ["branch", "checkout"]
        for marker in branch_markers:
            if marker in content:
                parts = content.split(marker)
                if len(parts) > 1:
                    branch_parts = parts[1].split()
                    if branch_parts:
                        info["branch"] = branch_parts[0].strip(".,;:\"'")
                        break
        
        return info
    
    def clone_repository(self, 
                        repo_url: str, 
                        clone_dir: Optional[str] = None, 
                        branch: Optional[str] = None) -> Dict[str, Any]:
        """
        Clone a GitHub repository
        
        Args:
            repo_url: URL or username/repo of the GitHub repository
            clone_dir: Directory where to clone the repository (optional)
            branch: Branch to clone (optional)
            
        Returns:
            Dictionary with clone operation results
        """
        logger.info(f"Cloning repository: {repo_url} to {clone_dir or 'default directory'}")
        
        # Normalize the repository URL
        if not repo_url.startswith(("http://", "https://", "git@")):
            if "/" in repo_url:
                # Assume it's in format username/repo
                repo_url = f"https://github.com/{repo_url}"
            else:
                error_msg = f"Invalid repository URL format: {repo_url}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "message": error_msg
                }
        
        # Extract repository name from URL for default directory name
        repo_name = repo_url.split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        
        # Set the clone directory if not provided
        if not clone_dir:
            clone_dir = os.path.join(CONFIG["clone_base_dir"], repo_name)
        
        # Use our existing clone function
        try:
            result = clone_github_repo(repo_url, clone_dir)
            
            # If branch specified, try to checkout after cloning
            if branch and os.path.exists(clone_dir):
                try:
                    import subprocess
                    subprocess.run(
                        ["git", "-C", clone_dir, "checkout", branch],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    logger.info(f"Checked out branch {branch}")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to checkout branch {branch}: {e}")
                    
            if os.path.exists(clone_dir):
                logger.info(f"Successfully cloned repository to {clone_dir}")
                # Update the current repository
                self.current_repository = os.path.abspath(clone_dir)
                return {
                    "success": True,
                    "message": f"Repository '{repo_url}' cloned successfully to {clone_dir}",
                    "path": self.current_repository
                }
            else:
                error_msg = f"Failed to clone repository: {repo_url}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "message": error_msg
                }
        except Exception as e:
            error_msg = f"Error cloning repository: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg
            }
    
    def inspect_repository(self, repo_path: str = None, query: str = None) -> Dict[str, Any]:
        """
        Inspect a cloned repository
        
        Args:
            repo_path: Path to the repository to inspect
            query: Free text query about what to inspect in the repository
            
        Returns:
            Dictionary with inspection results
        """
        if not repo_path and not self.current_repository:
            return {
                "success": False,
                "message": "No repository specified and no recently cloned repository available"
            }
        
        target_path = repo_path or self.current_repository
        
        if not os.path.exists(target_path):
            return {
                "success": False,
                "message": f"Repository path does not exist: {target_path}"
            }
        
        logger.info(f"Inspecting repository at {target_path}")
        
        # Get repository structure
        structure = self._get_repo_structure(target_path)
        
        # Look for README file
        readme_content = self._find_readme(target_path)
        
        # Get key files based on common file patterns
        key_files = self._find_key_files(target_path)
        
        result = {
            "success": True,
            "repo_path": target_path,
            "structure": structure,
            "readme": readme_content,
            "key_files": key_files
        }
        
        # If there's a specific query, add targeted information
        if query:
            result["query_response"] = self._process_query(target_path, query)
        
        return result
    
    def find_files(self, repo_path: str = None, pattern: str = "*") -> Dict[str, Any]:
        """
        Find files in the repository matching a pattern
        
        Args:
            repo_path: Path to the repository
            pattern: File pattern to search for (glob pattern)
            
        Returns:
            Dictionary with file search results
        """
        import glob
        
        if not repo_path and not self.current_repository:
            return {
                "success": False,
                "message": "No repository specified and no recently cloned repository available"
            }
        
        target_path = repo_path or self.current_repository
        
        if not os.path.exists(target_path):
            return {
                "success": False,
                "message": f"Repository path does not exist: {target_path}"
            }
        
        search_pattern = os.path.join(target_path, "**", pattern)
        files = [os.path.relpath(f, target_path) for f in glob.glob(search_pattern, recursive=True) if os.path.isfile(f)]
        
        return {
            "success": True,
            "repo_path": target_path,
            "pattern": pattern,
            "files": files,
            "count": len(files)
        }
    
    def read_file_content(self, repo_path: str = None, file_path: str = None) -> Dict[str, Any]:
        """
        Read the content of a file in the repository
        
        Args:
            repo_path: Path to the repository
            file_path: Path to the file relative to the repository
            
        Returns:
            Dictionary with file content
        """
        if not repo_path and not self.current_repository:
            return {
                "success": False,
                "message": "No repository specified and no recently cloned repository available"
            }
        
        target_repo = repo_path or self.current_repository
        
        if not os.path.exists(target_repo):
            return {
                "success": False,
                "message": f"Repository path does not exist: {target_repo}"
            }
        
        if not file_path:
            return {
                "success": False,
                "message": "No file path specified"
            }
        
        # Handle both absolute and relative paths
        full_path = file_path if os.path.isabs(file_path) else os.path.join(target_repo, file_path)
        
        if not os.path.exists(full_path):
            return {
                "success": False,
                "message": f"File does not exist: {full_path}"
            }
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "repo_path": target_repo,
                "file_path": file_path,
                "content": content
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error reading file: {str(e)}"
            }
    
    def _get_repo_structure(self, path: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Get the structure of a repository up to a certain depth
        
        Args:
            path: Path to the repository
            max_depth: Maximum directory depth to traverse
            
        Returns:
            Dictionary representing the repository structure
        """
        structure = {}
        
        def _traverse(current_path, depth, current_dict):
            if depth > max_depth:
                return
            
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                
                # Skip hidden files and directories
                if item.startswith('.'):
                    continue
                
                if os.path.isdir(item_path):
                    current_dict[item] = {}
                    _traverse(item_path, depth + 1, current_dict[item])
                else:
                    current_dict[item] = None
        
        _traverse(path, 1, structure)
        return structure
    
    def _find_readme(self, path: str) -> Optional[str]:
        """
        Find and read the README file in a repository
        
        Args:
            path: Path to the repository
            
        Returns:
            Content of the README file if found, None otherwise
        """
        readme_patterns = ['README.md', 'README', 'README.txt', 'Readme.md']
        
        for pattern in readme_patterns:
            readme_path = os.path.join(path, pattern)
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    logger.warning(f"Error reading README file: {str(e)}")
                    continue
        
        return None
    
    def _find_key_files(self, path: str) -> Dict[str, List[str]]:
        """
        Find key files in the repository by category
        
        Args:
            path: Path to the repository
            
        Returns:
            Dictionary of key files by category
        """
        key_files = {
            "configuration": [],
            "documentation": [],
            "source_code": [],
            "build": [],
            "tests": []
        }
        
        # Define patterns for each category
        patterns = {
            "configuration": ['*.json', '*.yaml', '*.yml', '*.ini', '*.conf', '*.toml', '*.xml', '.env*'],
            "documentation": ['*.md', '*.txt', '*.rst', '*.doc', '*.pdf'],
            "source_code": ['*.py', '*.js', '*.ts', '*.java', '*.c', '*.cpp', '*.go', '*.rs', '*.rb', '*.php', '*.cs'],
            "build": ['Makefile', 'setup.py', 'package.json', 'build.gradle', 'pom.xml', 'Cargo.toml', 'CMakeLists.txt'],
            "tests": ['test_*.py', '*_test.py', '*_test.go', '*_spec.js', '*_spec.ts', '*Test.java']
        }
        
        import glob
        
        for category, file_patterns in patterns.items():
            for pattern in file_patterns:
                search_pattern = os.path.join(path, "**", pattern)
                files = [os.path.relpath(f, path) for f in glob.glob(search_pattern, recursive=True) if os.path.isfile(f)]
                key_files[category].extend(files)
        
        return key_files
    
    def _process_query(self, repo_path: str, query: str) -> Dict[str, Any]:
        """
        Process a free text query about a repository
        
        Args:
            repo_path: Path to the repository
            query: Free text query
            
        Returns:
            Dictionary with query response
        """
        query_lower = query.lower()
        response = {}
        
        # Look for code samples based on keywords in the query
        if any(kw in query_lower for kw in ["code", "example", "function", "class", "implementation"]):
            file_types = []
            for lang in ["python", "py", "javascript", "js", "typescript", "ts", "java", "go", "rust", "c++", "cpp"]:
                if lang in query_lower:
                    if lang == "python" or lang == "py":
                        file_types.append("*.py")
                    elif lang == "javascript" or lang == "js":
                        file_types.append("*.js")
                    elif lang == "typescript" or lang == "ts":
                        file_types.append("*.ts")
                    elif lang == "java":
                        file_types.append("*.java")
                    elif lang == "go":
                        file_types.append("*.go")
                    elif lang == "rust":
                        file_types.append("*.rs")
                    elif lang in ["c++", "cpp"]:
                        file_types.extend(["*.cpp", "*.hpp", "*.cc", "*.h"])
            
            # If no specific language was mentioned, search across common file types
            if not file_types:
                file_types = ["*.py", "*.js", "*.ts", "*.java", "*.go", "*.rs", "*.cpp"]
            
            code_samples = []
            import glob
            
            for pattern in file_types:
                search_pattern = os.path.join(repo_path, "**", pattern)
                files = [f for f in glob.glob(search_pattern, recursive=True) if os.path.isfile(f)]
                
                # Limit to first 5 files for each type
                for file_path in files[:5]:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        rel_path = os.path.relpath(file_path, repo_path)
                        code_samples.append({
                            "path": rel_path,
                            "content": content[:2000] + ("..." if len(content) > 2000 else "")
                        })
                    except Exception:
                        continue
            
            response["code_samples"] = code_samples[:10]  # Limit to 10 samples total
        
        # Look for specific files mentioned in the query
        import re
        file_matches = re.findall(r'\b[\w\-\.]+\.\w+\b', query)
        if file_matches:
            specific_files = []
            for file_name in file_matches:
                search_pattern = os.path.join(repo_path, "**", file_name)
                files = [f for f in glob.glob(search_pattern, recursive=True) if os.path.isfile(f)]
                
                for file_path in files:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        rel_path = os.path.relpath(file_path, repo_path)
                        specific_files.append({
                            "path": rel_path,
                            "content": content[:2000] + ("..." if len(content) > 2000 else "")
                        })
                    except Exception:
                        continue
            
            response["specific_files"] = specific_files
        
        # Count lines of code by language
        if "lines" in query_lower or "loc" in query_lower or "count" in query_lower:
            extensions = {
                ".py": "Python",
                ".js": "JavaScript",
                ".ts": "TypeScript",
                ".java": "Java",
                ".go": "Go",
                ".rs": "Rust",
                ".cpp": "C++",
                ".c": "C",
                ".h": "C/C++ Header",
                ".hpp": "C++ Header",
                ".cs": "C#",
                ".rb": "Ruby",
                ".php": "PHP",
                ".html": "HTML",
                ".css": "CSS",
                ".md": "Markdown",
                ".json": "JSON",
                ".yml": "YAML",
                ".yaml": "YAML",
                ".xml": "XML"
            }
            
            loc_count = {}
            
            for root, _, files in os.walk(repo_path):
                for file in files:
                    _, ext = os.path.splitext(file)
                    if ext in extensions:
                        lang = extensions[ext]
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                line_count = sum(1 for _ in f)
                            
                            loc_count[lang] = loc_count.get(lang, 0) + line_count
                        except Exception:
                            continue
            
            response["lines_of_code"] = loc_count
        
        return response
    
    def handle_inspect_request(self, messages: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Handle a repository inspection request
        
        Args:
            messages: List of messages in the conversation
            
        Returns:
            Response message
        """
        if not messages:
            return {"content": "No messages provided."}
        
        last_message = messages[-1]
        query = last_message.get("content", "")
        
        if not self.current_repository:
            return {
                "content": "No repository has been cloned yet. Please clone a repository first."
            }
        
        # Call the inspect function
        result = self.inspect_repository(self.current_repository, query)
        
        if not result["success"]:
            return {
                "content": f"❌ {result['message']}"
            }
        
        # Format the response
        response = f"📁 Repository inspection results for: {os.path.basename(self.current_repository)}\n\n"
        
        # Add README content if available
        if result.get("readme"):
            readme_excerpt = result["readme"][:500] + "..." if len(result["readme"]) > 500 else result["readme"]
            response += f"📝 README Summary:\n{readme_excerpt}\n\n"
        
        # Add key files information
        if result.get("key_files"):
            response += "🔑 Key Files:\n"
            for category, files in result["key_files"].items():
                if files:
                    file_list = ", ".join(files[:5])
                    if len(files) > 5:
                        file_list += f" and {len(files) - 5} more"
                    response += f"- {category.capitalize()}: {file_list}\n"
        
        # Add query-specific information
        if result.get("query_response"):
            qr = result["query_response"]
            
            # Add code samples
            if qr.get("code_samples"):
                response += "\n💻 Code Samples:\n"
                for sample in qr["code_samples"][:3]:  # Limit to 3 samples in the response
                    response += f"- {sample['path']}\n"
                    if len(qr["code_samples"]) > 3:
                        response += f"  (and {len(qr['code_samples']) - 3} more samples)\n"
            
            # Add specific files
            if qr.get("specific_files"):
                response += "\n📄 Requested Files:\n"
                for file in qr["specific_files"]:
                    response += f"- {file['path']}\n"
            
            # Add lines of code count
            if qr.get("lines_of_code"):
                response += "\n📊 Lines of Code:\n"
                for lang, count in qr["lines_of_code"].items():
                    response += f"- {lang}: {count} lines\n"
        
        return {"content": response}
    
    def handle_clone_request(self, messages: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Handle a repository clone request
        
        Args:
            messages: List of messages in the conversation
            
        Returns:
            Response message
        """
        if not messages:
            return {"content": "No messages provided."}
        
        last_message = messages[-1]
        content = last_message.get("content", "")
        
        # Extract repository information from the message
        repo_info = self._extract_repo_info(content)
        
        if not repo_info["repo_url"]:
            return {
                "content": "I need a GitHub repository URL or username/repo to clone. Please provide this information."
            }
        
        # Call the clone function
        result = self.clone_repository(
            repo_url=repo_info["repo_url"],
            clone_dir=repo_info["clone_dir"],
            branch=repo_info["branch"]
        )
        
        if result["success"]:
            # Store the current repository path
            self.current_repository = result.get("path", None)
            return {
                "content": f"✅ {result['message']}\n\nYou can now ask me questions about the repository content and structure."
            }
        else:
            return {
                "content": f"❌ {result['message']}"
            }
    
def create_github_agents(use_llm: bool = True, llm_config: Dict[str, Any] = None) -> Dict[str, Agent]:
    """
    Create and configure the agents for GitHub operations.
    
    Args:
        use_llm: Whether to use an LLM for the assistant. If False, will create agents without LLM config.
               This is useful for testing without API keys.
        llm_config: Optional configuration for the LLM. If provided, will override the default configuration.
    
    Returns:
        Dict containing all the created agents
    """
    # Default LLM configuration
    _llm_config = False  # Default to no LLM
    
    if use_llm:
        if llm_config:
            _llm_config = llm_config
            logger.info("Using provided LLM configuration")
        elif "AZURE_OPENAI_API_KEY" in os.environ and "AZURE_OPENAI_ENDPOINT" in os.environ:
            # Configure for Azure OpenAI
            api_key = os.environ["AZURE_OPENAI_API_KEY"]
            endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
            deployment_name = os.environ.get("DEPLOYMENT_NAME", "Phi-4-mini-instruct")
            
            _llm_config = {
                "config_list": [{
                    "model": deployment_name,
                    "api_type": "azure",
                    "api_key": api_key,
                    "api_version": "2023-07-01-preview",  # Update this to your Azure OpenAI API version
                    "api_base": endpoint,
                    "deployment_name": deployment_name
                }]
            }
            logger.info("Using Azure OpenAI configuration with API key")
        else:
            logger.warning("No Azure OpenAI API key or endpoint found. Creating agents without LLM capabilities.")
    
    # Create a code assistant agent
    assistant = AssistantAgent(
        name="assistant",
        system_message="""You are a helpful AI assistant that specializes in GitHub operations.
        You can help with cloning repositories, understanding git commands, and analyzing repository content.
        When asked to inspect or analyze a repository, provide detailed insights about the code structure, 
        key components, frameworks used, and important files.""",
        llm_config=_llm_config
    )
    
    # Create the GitHub clone agent
    github_agent = GitHubCloneAgent(
        name="github_clone_agent",
        human_input_mode="NEVER",
        system_message="""I am a GitHub clone agent that can help clone repositories from GitHub.
        Tell me which repository you want to clone, and I'll handle it for you.
        After cloning, I can inspect the repository structure and contents based on your questions."""
    )
    
    # Create user proxy agent
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="ALWAYS",
        system_message="You are interacting with a GitHub assistant and a GitHub clone agent."
    )
    
    logger.info("GitHub agents created successfully")
    return {
        "assistant": assistant,
        "github_agent": github_agent,
        "user_proxy": user_proxy
    }