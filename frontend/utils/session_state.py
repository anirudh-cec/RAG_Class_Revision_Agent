"""Session state management utilities for Streamlit."""
from typing import Any, List, Dict, Optional
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.logger.custom_logger import CustomLogger
from src.exception.custom_exception import RagAppException


logger = CustomLogger(log_dir="logs").get_logger(__name__)

# Default session state values
DEFAULT_STATE = {
    "current_step": 0,
    "vtt_files": [],
    "code_files": [],
    "github_urls": [],
    "github_branches": {},  # url -> branch mapping
    "has_code_files": None,  # None = not decided, True/False = decided
    "has_github_repos": None,
    "processing": False,
    "completed": False,
    "errors": [],
    "docs_path": None,
    "upload_stats": {
        "vtt_saved": [],
        "code_saved": [],
        "github_fetched": []
    }
}


def init_session_state() -> None:
    """
    Initialize all required session state variables with default values.
    Only sets values that don't already exist.
    """
    try:
        logger.info("Initializing session state")

        for key, default_value in DEFAULT_STATE.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
                logger.debug("Session state initialized", key=key, value=default_value)

        logger.info("Session state initialization complete")

    except Exception as e:
        logger.error("Failed to initialize session state", error=str(e))
        raise RagAppException(f"Failed to initialize session state: {str(e)}", e)


def reset_session_state() -> None:
    """
    Reset all session state to default values.
    This clears all user data and returns to initial state.
    """
    try:
        logger.info("Resetting session state")

        for key, default_value in DEFAULT_STATE.items():
            st.session_state[key] = default_value

        logger.info("Session state reset complete")

    except Exception as e:
        logger.error("Failed to reset session state", error=str(e))
        raise RagAppException(f"Failed to reset session state: {str(e)}", e)


def get_state(key: str) -> Any:
    """
    Get a value from session state.

    Args:
        key: Session state key

    Returns:
        Value from session state, or None if not found
    """
    try:
        value = st.session_state.get(key)
        logger.debug("Session state retrieved", key=key)
        return value
    except Exception as e:
        logger.error("Failed to get session state", key=key, error=str(e))
        return None


def set_state(key: str, value: Any) -> None:
    """
    Set a value in session state.

    Args:
        key: Session state key
        value: Value to set
    """
    try:
        st.session_state[key] = value
        logger.debug("Session state set", key=key)
    except Exception as e:
        logger.error("Failed to set session state", key=key, error=str(e))
        raise RagAppException(f"Failed to set session state: {str(e)}", e)


def add_to_list(key: str, value: Any) -> None:
    """
    Add an item to a list in session state.

    Args:
        key: Session state key for the list
        value: Value to add
    """
    try:
        current_list = st.session_state.get(key, [])
        if not isinstance(current_list, list):
            current_list = []
        current_list.append(value)
        st.session_state[key] = current_list
        logger.debug("Item added to list", key=key, list_length=len(current_list))
    except Exception as e:
        logger.error("Failed to add to list", key=key, error=str(e))
        raise RagAppException(f"Failed to add to list: {str(e)}", e)


def remove_from_list(key: str, index: int) -> None:
    """
    Remove an item from a list in session state by index.

    Args:
        key: Session state key for the list
        index: Index of item to remove
    """
    try:
        current_list = st.session_state.get(key, [])
        if not isinstance(current_list, list):
            return

        if 0 <= index < len(current_list):
            removed_item = current_list.pop(index)
            st.session_state[key] = current_list
            logger.debug("Item removed from list", key=key, index=index, removed=removed_item)
        else:
            logger.warning("Invalid index for removal", key=key, index=index, list_length=len(current_list))
    except Exception as e:
        logger.error("Failed to remove from list", key=key, index=index, error=str(e))
        raise RagAppException(f"Failed to remove from list: {str(e)}", e)


def get_current_step() -> int:
    """
    Get the current step from session state.

    Returns:
        Current step number (0-5)
    """
    return get_state("current_step") or 0


def set_current_step(step: int) -> None:
    """
    Set the current step in session state.

    Args:
        step: Step number (0-5)
    """
    set_state("current_step", step)
    logger.info("Current step updated", step=step)


def clear_errors() -> None:
    """Clear all errors from session state."""
    set_state("errors", [])


def add_error(error_message: str) -> None:
    """
    Add an error message to session state.

    Args:
        error_message: Error message to add
    """
    add_to_list("errors", error_message)
    logger.error("Error added to session", error_message=error_message)


def get_errors() -> List[str]:
    """
    Get all errors from session state.

    Returns:
        List of error messages
    """
    return get_state("errors") or []
