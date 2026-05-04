"""Code file upload page (Step 2)."""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.logger.custom_logger import CustomLogger
from src.exception.custom_exception import RagAppException
from frontend.components.step_indicator import render_step_indicator
from frontend.components.file_uploader import render_code_uploader
from frontend.utils.session_state import set_current_step, get_state, set_state


logger = CustomLogger(log_dir="logs").get_logger(__name__)


def render():
    """Render the code upload page."""
    try:
        logger.info("Rendering code upload page (Step 2)")

        # Render step indicator
        render_step_indicator(current_step=2)

        st.markdown("## 💻 Upload Code Files (Optional)")
        st.markdown(
            "Do you have any code files that were discussed in the class? "
            "These files are optional but help provide context for better answers."
        )

        st.markdown("---")

        # Check if user already made a decision
        has_code_files = get_state("has_code_files")

        if has_code_files is None:
            # Show selection buttons
            st.markdown("#### Do you have code files to upload?")

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                if st.button("✅ Yes, I have code files", use_container_width=True):
                    set_state("has_code_files", True)
                    st.rerun()

            with col2:
                if st.button("❌ No, skip this step", use_container_width=True):
                    set_state("has_code_files", False)
                    set_state("code_files", [])  # Clear any existing code files
                    st.rerun()

            st.info("💡 Select an option above to continue")

        elif has_code_files:
            # Show code file uploader
            st.success("✅ Code files enabled - upload your files below")

            # Get existing code files
            existing_files = get_state("code_files") or []

            # Render uploader
            uploaded_files = render_code_uploader()

            # Update session state
            if uploaded_files:
                set_state("code_files", uploaded_files)
                logger.info(f"Code files in session: {len(uploaded_files)}")

            # Option to skip
            st.markdown("---")
            if st.button("🚫 Skip and continue without code files"):
                set_state("has_code_files", False)
                set_state("code_files", [])
                st.rerun()

        else:
            # User chose to skip
            st.info("⏭️ Code file upload skipped (optional)")

            if st.button("🔄 Change my mind - add code files"):
                set_state("has_code_files", None)
                st.rerun()

        st.markdown("---")

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("← Back to VTT", use_container_width=True):
                logger.info("Going back to VTT upload page")
                set_current_step(1)
                st.rerun()

        with col3:
            # Enable continue if user has made a decision
            can_continue = has_code_files is not None

            if st.button(
                "Continue to GitHub →",
                type="primary",
                use_container_width=True,
                disabled=not can_continue
            ):
                logger.info("Proceeding to GitHub upload step")
                set_current_step(3)
                st.rerun()

        logger.info("Code upload page rendered successfully")

    except Exception as e:
        logger.error(f"Error rendering code upload page: {str(e)}")
        st.error("An error occurred while loading the page. Please refresh and try again.")
