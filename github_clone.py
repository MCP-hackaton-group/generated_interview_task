import subprocess
import os
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("github_clone")

def clone_github_repo(repo_url: str, clone_dir: str = "./cloned_repo", branch: str = None):
    """
    Clone a GitHub repository.
    
    Args:
        repo_url: URL of the GitHub repository to clone
        clone_dir: Directory where to clone the repository
        branch: Branch to checkout after cloning (optional)
        
    Returns:
        Dictionary with clone operation results
    """
    result = {
        "success": False,
        "message": "",
        "repo_dir": clone_dir
    }
    
    # Check if git is installed
    if not shutil.which("git"):
        result["message"] = "Git is not installed or not in PATH."
        logger.error(result["message"])
        return result

    # Check if directory already exists
    if os.path.exists(clone_dir):
        result["message"] = f"Directory '{clone_dir}' already exists."
        logger.error(result["message"])
        return result
    
    try:
        # Clone the repository
        subprocess.run(["git", "clone", repo_url, clone_dir], check=True, 
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(f"Repository cloned to {clone_dir}")
        
        # Checkout specific branch if requested
        if branch:
            subprocess.run(["git", "-C", clone_dir, "checkout", branch], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"Checked out branch: {branch}")
        
        result["success"] = True
        result["message"] = f"Repository '{repo_url}' cloned successfully to {clone_dir}"
        return result
    
    except subprocess.CalledProcessError as e:
        result["message"] = f"Failed to clone repository: {e}"
        logger.error(result["message"])
        return result
    except Exception as e:
        result["message"] = f"Unexpected error: {str(e)}"
        logger.error(result["message"])
        return result

# Example usage when script is run directly
if __name__ == "__main__":
    repo_url = "https://github.com/adielashrov/trust-ai-roma-for-llm"
    result = clone_github_repo(repo_url, "./cloned_repo_example")
    print(f"Clone {'succeeded' if result['success'] else 'failed'}: {result['message']}")