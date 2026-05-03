"""GitHub URL input component for adding repository links."""
import streamlit as st
from typing import List, Tuple, Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.logger.custom_logger import CustomLogger
from src.exception.custom_exception import RagAppException
from frontend.utils.validators import validate_github_url


logger = CustomLogger(log_dir="logs").get_logger(__name__)


def render_github_inputs() -> Tuple[List[str], Dict[str, str]]:
    """
    Render the GitHub URL input component with dynamic fields.

    Returns:
        Tuple of (urls, branches) where urls is a list of valid GitHub URLs
        and branches is a dict mapping URL to branch name
    """
    try:
        logger.debug("Rendering GitHub inputs")

        # Initialize session state for GitHub URLs if not exists
        if 'github_input_count' not in st.session_state:
            st.session_state.github_input_count = 1
            st.session_state.github_url_values = {0: ""}
            st.session_state.github_branch_values = {0: "main"}
            st.session_state.github_validity = {0: None}

        urls = []
        branches = {}

        # Header
        st.markdown("#### Repository URLs")
        st.markdown("Enter the GitHub repository URLs you want to include.")

        # Render URL input fields
        valid_count = 0
        for i in range(st.session_state.github_input_count):
            col1, col2, col3 = st.columns([3, 1, 0.5])

            with col1:
                # URL input
                current_url = st.session_state.github_url_values.get(i, "")
                url = st.text_input(
                    label=f"Repository URL {i + 1}",
                    value=current_url,
                    placeholder="https://github.com/owner/repo",
                    key=f"github_url_{i}",
                    label_visibility="collapsed"
                )

                # Validate URL
                is_valid, error_msg, parsed_data = validate_github_url(url)

                # Store URL and validity
                st.session_state.github_url_values[i] = url
                st.session_state.github_validity[i] = is_valid if url else None

                # Show validation feedback
                if url:
                    if is_valid:
                        st.markdown(f"✅ Valid: `{parsed_data['owner']}/{parsed_data['repo']}`")
                        valid_count += 1
                        urls.append(url)
                    else:
                        st.markdown(f"❌ {error_msg}")

            with col2:
                # Branch selector
                current_branch = st.session_state.github_branch_values.get(i, "main")
                branch = st.selectbox(
                    label=f"Branch {i + 1}",
                    options=["main", "master", "develop", "other"],
                    index=0 if current_branch == "main" else 1 if current_branch == "master" else 2 if current_branch == "develop" else 3,
                    key=f"github_branch_{i}",
                    label_visibility="collapsed"
                )

                if branch == "other":
                    custom_branch = st.text_input(
                        label="Custom branch",
                        value="",
                        placeholder="branch-name",
                        key=f"github_branch_custom_{i}"
                    )
                    branch = custom_branch if custom_branch else "main"

                st.session_state.github_branch_values[i] = branch

                # Store branch for valid URLs
                if url and is_valid:
                    branches[url] = branch

            with col3:
                # Remove button (disabled if only one field)
                if st.session_state.github_input_count > 1:
                    if st.button("🗑️", key=f"remove_github_{i}", use_container_width=True):
                        # Remove this index
                        del st.session_state.github_url_values[i]
                        del st.session_state.github_branch_values[i]
                        del st.session_state.github_validity[i]

                        # Renumber remaining
                        new_urls = {}
                        new_branches = {}
                        new_validity = {}
                        new_idx = 0
                        for old_idx in sorted(st.session_state.github_url_values.keys()):
                            if old_idx != i:
                                new_urls[new_idx] = st.session_state.github_url_values[old_idx]
                                new_branches[new_idx] = st.session_state.github_branch_values[old_idx]
                                new_validity[new_idx] = st.session_state.github_validity[old_idx]
                                new_idx += 1

                        st.session_state.github_url_values = new_urls
                        st.session_state.github_branch_values = new_branches
                        st.session_state.github_validity = new_validity
                        st.session_state.github_input_count -= 1
                        st.rerun()

        # Add Another button
        if st.button("➕ Add Another Repository", key="add_github"):
            st.session_state.github_input_count += 1
            new_idx = st.session_state.github_input_count - 1
            st.session_state.github_url_values[new_idx] = ""
            st.session_state.github_branch_values[new_idx] = "main"
            st.session_state.github_validity[new_idx] = None
            st.rerun()

        # Summary
        if valid_count > 0:
            st.success(f"✅ {valid_count} valid repository URL(s) ready to fetch")
        else:
            st.info("💡 Add at least one valid GitHub repository URL to continue")

        logger.debug(f"GitHub inputs rendered, valid URLs: {len(urls)}")
        return urls, branches

    except Exception as e:
        logger.error(f"Failed to render GitHub inputs: {str(e)}")
        raise RagAppException(f"Failed to render GitHub inputs: {str(e)}", e)
