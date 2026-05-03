"""File handling utilities for saving uploaded files and fetching GitHub repos."""
import os
import shutil
import subprocess
import tempfile
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.logger.custom_logger import CustomLogger
from src.exception.custom_exception import RagAppException


logger = CustomLogger(log_dir="logs").get_logger(__name__)

DOCS_FOLDER_NAME = "docs"
VTT_SUBFOLDER = "vtt"
CODE_SUBFOLDER = "code"
GITHUB_SUBFOLDER = "github"


def ensure_docs_folder(base_path: Optional[str] = None) -> str:
    """
    Ensure the docs folder structure exists.

    Args:
        base_path: Base directory path. If None, uses current working directory.

    Returns:
        Path to the docs folder.
    """
    try:
        if base_path is None:
            base_path = os.getcwd()

        docs_path = os.path.join(base_path, DOCS_FOLDER_NAME)

        # Create subfolders
        for subfolder in [VTT_SUBFOLDER, CODE_SUBFOLDER, GITHUB_SUBFOLDER]:
            folder_path = os.path.join(docs_path, subfolder)
            os.makedirs(folder_path, exist_ok=True)

        logger.info("Docs folder structure ensured", docs_path=docs_path)
        return docs_path

    except Exception as e:
        logger.error("Failed to ensure docs folder", error=str(e))
        raise RagAppException(f"Failed to create docs folder: {str(e)}", e)


def save_vtt_files(files: List[Any], docs_path: str) -> List[str]:
    """
    Save uploaded VTT files to the docs/vtt/ folder.

    Args:
        files: List of uploaded file objects
        docs_path: Path to the docs folder

    Returns:
        List of saved file paths
    """
    saved_paths = []

    try:
        vtt_folder = os.path.join(docs_path, VTT_SUBFOLDER)

        for file in files:
            try:
                filename = getattr(file, 'name', 'unnamed.vtt')
                file_path = os.path.join(vtt_folder, filename)

                # Handle duplicate filenames
                counter = 1
                base_name, ext = os.path.splitext(filename)
                while os.path.exists(file_path):
                    new_filename = f"{base_name}_{counter}{ext}"
                    file_path = os.path.join(vtt_folder, new_filename)
                    counter += 1

                # Save file content
                content = file.read() if hasattr(file, 'read') else file.getvalue() if hasattr(file, 'getvalue') else b''
                with open(file_path, 'wb') as f:
                    if isinstance(content, bytes):
                        f.write(content)
                    else:
                        f.write(content.encode('utf-8'))

                saved_paths.append(file_path)
                logger.info("VTT file saved", file_path=file_path, original_name=filename)

            except Exception as e:
                logger.error("Failed to save VTT file", filename=getattr(file, 'name', 'unknown'), error=str(e))
                raise

        return saved_paths

    except Exception as e:
        logger.error("Failed to save VTT files", error=str(e))
        raise RagAppException(f"Failed to save VTT files: {str(e)}", e)


def save_code_files(files: List[Any], docs_path: str) -> List[str]:
    """
    Save uploaded code files to the docs/code/ folder.

    Args:
        files: List of uploaded file objects
        docs_path: Path to the docs folder

    Returns:
        List of saved file paths
    """
    saved_paths = []

    try:
        code_folder = os.path.join(docs_path, CODE_SUBFOLDER)

        for file in files:
            try:
                filename = getattr(file, 'name', 'unnamed.txt')
                file_path = os.path.join(code_folder, filename)

                # Handle duplicate filenames
                counter = 1
                base_name, ext = os.path.splitext(filename)
                while os.path.exists(file_path):
                    new_filename = f"{base_name}_{counter}{ext}"
                    file_path = os.path.join(code_folder, new_filename)
                    counter += 1

                # Save file content
                content = file.read() if hasattr(file, 'read') else file.getvalue() if hasattr(file, 'getvalue') else b''
                with open(file_path, 'wb') as f:
                    if isinstance(content, bytes):
                        f.write(content)
                    else:
                        f.write(content.encode('utf-8'))

                saved_paths.append(file_path)
                logger.info("Code file saved", file_path=file_path, original_name=filename)

            except Exception as e:
                logger.error("Failed to save code file", filename=getattr(file, 'name', 'unknown'), error=str(e))
                raise

        return saved_paths

    except Exception as e:
        logger.error("Failed to save code files", error=str(e))
        raise RagAppException(f"Failed to save code files: {str(e)}", e)


def fetch_github_repo(url: str, branch: str, docs_path: str) -> Dict[str, Any]:
    """
    Fetch a GitHub repository and save it to the docs/github/ folder.

    Args:
        url: GitHub repository URL
        branch: Branch name to fetch
        docs_path: Path to the docs folder

    Returns:
        Dictionary with success status, message, saved path, and file count
    """
    try:
        logger.info("Fetching GitHub repository", url=url, branch=branch)

        # Parse owner and repo from URL
        from .validators import validate_github_url
        is_valid, error_msg, parsed_data = validate_github_url(url)

        if not is_valid:
            logger.error("Invalid GitHub URL", url=url, error=error_msg)
            return {
                "success": False,
                "message": error_msg,
                "saved_path": None,
                "files_count": 0
            }

        owner = parsed_data["owner"]
        repo = parsed_data["repo"]

        # Create target folder
        github_folder = os.path.join(docs_path, GITHUB_SUBFOLDER)
        target_folder = os.path.join(github_folder, f"{owner}_{repo}")

        # Remove existing folder if it exists
        if os.path.exists(target_folder):
            shutil.rmtree(target_folder)

        os.makedirs(target_folder, exist_ok=True)

        # Clone the repository using git
        clone_url = f"https://github.com/{owner}/{repo}.git"

        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", branch, clone_url, target_folder],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            if result.returncode != 0:
                # Try without branch if branch doesn't exist
                if "Remote branch" in result.stderr:
                    logger.warning("Branch not found, trying default branch", branch=branch)
                    shutil.rmtree(target_folder)
                    os.makedirs(target_folder)
                    result = subprocess.run(
                        ["git", "clone", "--depth", "1", clone_url, target_folder],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )

                if result.returncode != 0:
                    raise Exception(f"Git clone failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.error("Git clone timed out", url=url)
            raise Exception("Repository clone timed out. Try a smaller repository.")

        # Remove .git folder to save space
        git_folder = os.path.join(target_folder, '.git')
        if os.path.exists(git_folder):
            shutil.rmtree(git_folder)

        # Count files
        files_count = sum([len(files) for _, _, files in os.walk(target_folder)])

        logger.info("GitHub repository fetched successfully",
                   url=url, target_folder=target_folder, files_count=files_count)

        return {
            "success": True,
            "message": f"Repository {owner}/{repo} fetched successfully",
            "saved_path": target_folder,
            "files_count": files_count
        }

    except Exception as e:
        logger.error("Failed to fetch GitHub repository", url=url, error=str(e))
        return {
            "success": False,
            "message": f"Failed to fetch repository: {str(e)}",
            "saved_path": None,
            "files_count": 0
        }


def cleanup_on_error(docs_path: str) -> None:
    """
    Clean up partially created docs folder on error.

    Args:
        docs_path: Path to the docs folder
    """
    try:
        if os.path.exists(docs_path):
            logger.warning("Cleaning up docs folder due to error", docs_path=docs_path)
            shutil.rmtree(docs_path)
    except Exception as e:
        logger.error("Failed to cleanup docs folder", docs_path=docs_path, error=str(e))


def get_storage_stats(docs_path: str) -> Dict[str, Any]:
    """
    Get storage statistics for the docs folder.

    Args:
        docs_path: Path to the docs folder

    Returns:
        Dictionary with total_size, file_count, breakdown by type
    """
    try:
        stats = {
            "total_size_bytes": 0,
            "total_size_mb": 0,
            "file_count": 0,
            "breakdown": {
                "vtt": {"count": 0, "size_bytes": 0},
                "code": {"count": 0, "size_bytes": 0},
                "github": {"count": 0, "size_bytes": 0}
            }
        }

        if not os.path.exists(docs_path):
            return stats

        for category in [VTT_SUBFOLDER, CODE_SUBFOLDER, GITHUB_SUBFOLDER]:
            category_path = os.path.join(docs_path, category)
            if os.path.exists(category_path):
                for root, _, files in os.walk(category_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(file_path)
                            stats["total_size_bytes"] += size
                            stats["file_count"] += 1
                            stats["breakdown"][category]["count"] += 1
                            stats["breakdown"][category]["size_bytes"] += size
                        except OSError:
                            pass

        stats["total_size_mb"] = round(stats["total_size_bytes"] / (1024 * 1024), 2)
        for category in stats["breakdown"]:
            stats["breakdown"][category]["size_mb"] = round(
                stats["breakdown"][category]["size_bytes"] / (1024 * 1024), 2
            )

        return stats

    except Exception as e:
        logger.error("Failed to get storage stats", docs_path=docs_path, error=str(e))
        raise RagAppException(f"Failed to get storage stats: {str(e)}", e)
