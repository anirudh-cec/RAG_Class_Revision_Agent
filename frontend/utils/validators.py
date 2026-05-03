"""Validation utilities for file uploads and inputs."""
from typing import Tuple, Dict, Any
import re
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.logger.custom_logger import CustomLogger
from src.exception.custom_exception import RagAppException


logger = CustomLogger(log_dir="logs").get_logger(__name__)

ALLOWED_CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c',
    '.go', '.rs', '.rb', '.php', '.sql', '.html', '.css', '.json',
    '.yaml', '.yml', '.md', '.txt', '.sh', '.bat', '.ps1'
}

MAX_VTT_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_CODE_FILE_SIZE = 10 * 1024 * 1024  # 10MB per file


def validate_vtt_file(file) -> Tuple[bool, str]:
    """
    Validate a VTT subtitle file.

    Args:
        file: Uploaded file object with 'name' and 'size' attributes

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        logger.info("Validating VTT file", filename=getattr(file, 'name', 'unknown'))

        filename = getattr(file, 'name', '')
        file_size = getattr(file, 'size', 0)

        if not filename.lower().endswith('.vtt'):
            logger.warning("VTT validation failed: invalid extension", filename=filename)
            return False, f"File '{filename}' is not a .vtt file"

        if file_size > MAX_VTT_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            max_mb = MAX_VTT_FILE_SIZE / (1024 * 1024)
            logger.warning("VTT validation failed: file too large",
                         filename=filename, size_mb=size_mb)
            return False, f"File '{filename}' is too large ({size_mb:.1f}MB, max {max_mb:.0f}MB)"

        logger.info("VTT validation passed", filename=filename, size_bytes=file_size)
        return True, ""

    except Exception as e:
        logger.error("Error during VTT validation", error=str(e))
        raise RagAppException(f"Failed to validate VTT file: {str(e)}", e)


def validate_code_file(file) -> Tuple[bool, str]:
    """
    Validate a code file.

    Args:
        file: Uploaded file object with 'name' and 'size' attributes

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        logger.info("Validating code file", filename=getattr(file, 'name', 'unknown'))

        filename = getattr(file, 'name', '')
        file_size = getattr(file, 'size', 0)

        # Check extension
        _, ext = os.path.splitext(filename.lower())
        if ext not in ALLOWED_CODE_EXTENSIONS:
            logger.warning("Code validation failed: extension not allowed",
                         filename=filename, extension=ext)
            allowed = ', '.join(sorted(ALLOWED_CODE_EXTENSIONS))[:100] + "..."
            return False, f"File '{filename}' has unsupported extension. Allowed: {allowed}"

        # Check size
        if file_size > MAX_CODE_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            max_mb = MAX_CODE_FILE_SIZE / (1024 * 1024)
            logger.warning("Code validation failed: file too large",
                         filename=filename, size_mb=size_mb)
            return False, f"File '{filename}' is too large ({size_mb:.1f}MB, max {max_mb:.0f}MB)"

        logger.info("Code validation passed", filename=filename,
                   extension=ext, size_bytes=file_size)
        return True, ""

    except Exception as e:
        logger.error("Error during code file validation", error=str(e))
        raise RagAppException(f"Failed to validate code file: {str(e)}", e)


def validate_github_url(url: str) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validate a GitHub repository URL.

    Args:
        url: GitHub repository URL string

    Returns:
        Tuple of (is_valid, error_message, parsed_data)
        parsed_data contains: owner, repo, normalized_url
    """
    try:
        logger.info("Validating GitHub URL", url=url[:50] if url else "empty")

        if not url or not isinstance(url, str):
            logger.warning("GitHub validation failed: empty or invalid URL")
            return False, "URL is required", {}

        url = url.strip()

        # Normalize URL
        # Remove trailing .git if present
        if url.endswith('.git'):
            url = url[:-4]
        # Remove trailing slash
        url = url.rstrip('/')

        # Check if it's a GitHub URL
        if not url.startswith('https://github.com/'):
            logger.warning("GitHub validation failed: not a GitHub URL", url=url[:50])
            return False, "URL must start with https://github.com/", {}

        # Extract path parts
        path_part = url[len('https://github.com/'):]
        if not path_part:
            logger.warning("GitHub validation failed: empty path")
            return False, "Invalid GitHub URL format", {}

        parts = path_part.split('/')
        if len(parts) < 2:
            logger.warning("GitHub validation failed: insufficient path parts", parts=parts)
            return False, "URL must be in format: https://github.com/owner/repo", {}

        owner = parts[0]
        repo = parts[1]

        # Validate owner and repo names
        # GitHub allows: alphanumeric, hyphens, underscores
        # Cannot start or end with hyphen
        valid_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$'

        if not re.match(valid_pattern, owner):
            logger.warning("GitHub validation failed: invalid owner name", owner=owner)
            return False, f"Invalid repository owner name: '{owner}'", {}

        if not re.match(valid_pattern, repo):
            logger.warning("GitHub validation failed: invalid repo name", repo=repo)
            return False, f"Invalid repository name: '{repo}'", {}

        normalized_url = f"https://github.com/{owner}/{repo}"
        parsed_data = {
            "owner": owner,
            "repo": repo,
            "normalized_url": normalized_url
        }

        logger.info("GitHub validation passed", owner=owner, repo=repo)
        return True, "", parsed_data

    except Exception as e:
        logger.error("Error during GitHub URL validation", error=str(e))
        raise RagAppException(f"Failed to validate GitHub URL: {str(e)}", e)
