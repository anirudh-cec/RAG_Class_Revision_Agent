"""GitHub repository upload page (Step 3)."""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.logger.custom_logger import CustomLogger
from src.exception.custom_exception import RagAppException
from frontend.components.step_indicator import render_step_indicator
from frontend.components.github_input import render_github_inputs
from frontend.utils.session_state import set_current_step, get_state, set_state


logger = CustomLogger(log_dir="logs").get_logger(__name__)


def render():
    """Render the GitHub upload page."""
    try:
        logger.info("Rendering GitHub upload page (Step 3)")

        # Render step indicator
        render_step_indicator(current_step=3)

        st.markdown("## 🐙 Add GitHub Repositories (Optional)")
        st.markdown(
            "Do you have any GitHub repositories you'd like to include? "
            "This is optional but helps provide additional context for your class materials."
        )

        st.markdown("---")

        # Check if user already made a decision
        has_github_repos = get_state("has_github_repos")

        if has_github_repos is None:
            # Show selection buttons
            st.markdown("#### Do you have GitHub repositories to add?")

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                if st.button("✅ Yes, I have repositories", use_container_width=True):
                    set_state("has_github_repos", True)
                    st.rerun()

            with col2:
                if st.button("❌ No, skip this step", use_container_width=True):
                    set_state("has_github_repos", False)
                    set_state("github_urls", [])
                    set_state("github_branches", {})
                    st.rerun()

            st.info("💡 Select an option above to continue")

        elif has_github_repos:
            # Show GitHub URL inputs
            st.success("✅ GitHub repositories enabled - add your URLs below")

            # Render GitHub URL inputs
            urls, branches = render_github_inputs()

            # Update session state
            if urls:
                set_state("github_urls", urls)
                set_state("github_branches", branches)
                logger.info(f"GitHub URLs in session: {len(urls)}")

            # Option to skip
            st.markdown("---")
            if st.button("🚫 Skip and continue without GitHub repos"):
                set_state("has_github_repos", False)
                set_state("github_urls", [])
                set_state("github_branches", {})
                st.rerun()

        else:
            # User chose to skip
            st.info("⏭️ GitHub repository upload skipped (optional)")

            if st.button("🔄 Change my mind - add repositories"):
                set_state("has_github_repos", None)
                st.rerun()

        st.markdown("---")

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("← Back to Code Files", use_container_width=True):
                logger.info("Going back to code upload page")
                set_current_step(2)
                st.rerun()

        with col3:
            # Enable continue if user has made a decision
            can_continue = has_github_repos is not None

            if st.button(
                "Continue to Review →",
                type="primary",
                use_container_width=True,
                disabled=not can_continue
            ):
                logger.info("Proceeding to review page")
                set_current_step(4)
                st.rerun()

        logger.info("GitHub upload page rendered successfully")

    except Exception as e:
        logger.error(f"Error rendering GitHub upload page: {str(e)}")
        st.error("An error occurred while loading the page. Please refresh and try again.")
