"""VTT upload page (Step 1)."""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.logger.custom_logger import CustomLogger
from src.exception.custom_exception import RagAppException
from frontend.components.step_indicator import render_step_indicator
from frontend.components.file_uploader import render_vtt_uploader, preview_file_content
from frontend.utils.session_state import set_current_step, get_state, set_state


logger = CustomLogger(log_dir="logs").get_logger(__name__)


def render():
    """Render the VTT upload page."""
    try:
        logger.info("Rendering VTT upload page (Step 1)")

        # Render step indicator
        render_step_indicator(current_step=1)

        st.markdown("## 📄 Upload VTT Subtitle Files")
        st.markdown(
            "Upload the subtitle files from your class recordings. "
            "These files help us understand the content of your classes."
        )

        st.markdown("---")

        # Get existing VTT files from session
        existing_files = get_state("vtt_files") or []

        # Render uploader
        uploaded_files = render_vtt_uploader()

        # Update session state with valid files
        if uploaded_files:
            set_state("vtt_files", uploaded_files)
            logger.info(f"VTT files in session: {len(uploaded_files)}")

        # File preview section (if files uploaded)
        current_files = uploaded_files if uploaded_files else existing_files
        if current_files:
            st.markdown("---")
            with st.expander("👁️ Preview first file"):
                preview = preview_file_content(current_files[0], max_chars=800)
                if preview:
                    st.text_area("Content Preview", value=preview, height=200, disabled=True)
                else:
                    st.info("Preview not available for this file type")

        st.markdown("---")

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("← Back to Start", use_container_width=True):
                logger.info("Going back to landing page")
                set_current_step(0)
                st.rerun()

        with col3:
            has_files = len(current_files) > 0
            if st.button(
                "Continue to Code Files →",
                type="primary",
                use_container_width=True,
                disabled=not has_files
            ):
                logger.info("Proceeding to code upload step")
                set_current_step(2)
                st.rerun()

        # Show error if trying to continue without files
        if not has_files:
            st.warning("⚠️ Please upload at least one VTT file to continue")

        logger.info("VTT upload page rendered successfully")

    except Exception as e:
        logger.error(f"Error rendering VTT upload page: {str(e)}")
        st.error("An error occurred while loading the page. Please refresh and try again.")
