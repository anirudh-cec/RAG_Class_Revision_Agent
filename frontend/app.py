"""Main entry point for the Streamlit frontend application."""
import streamlit as st
import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env
load_dotenv()

from src.logger.custom_logger import CustomLogger
from src.exception.custom_exception import RagAppException
from frontend.utils.session_state import init_session_state, get_current_step
from frontend.styles.custom_css import get_custom_css

# Import pages
from frontend.pages import landing, vtt_upload, code_upload, github_upload, review, success


# Initialize logger
logger = CustomLogger(log_dir="logs").get_logger(__name__)


def main():
    """Main application entry point."""
    try:
        # Page configuration
        st.set_page_config(
            page_title="Class Recording RAG",
            page_icon="📚",
            layout="wide",
            initial_sidebar_state="collapsed"
        )

        # Inject custom CSS
        st.markdown(get_custom_css(), unsafe_allow_html=True)

        # Initialize session state
        init_session_state()

        # Get current step
        current_step = get_current_step()
        logger.info(f"Current step: {current_step}")

        # Route to appropriate page
        if current_step == 0:
            landing.render()
        elif current_step == 1:
            vtt_upload.render()
        elif current_step == 2:
            code_upload.render()
        elif current_step == 3:
            github_upload.render()
        elif current_step == 4:
            review.render()
        elif current_step == 5:
            success.render()
        else:
            logger.error(f"Invalid step: {current_step}")
            st.error("An error occurred. Please restart the application.")

    except RagAppException as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
        st.button("🔄 Restart", on_click=lambda: init_session_state())

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        st.error("An unexpected error occurred. Please check the logs and try again.")
        st.button("🔄 Restart", on_click=lambda: init_session_state())


if __name__ == "__main__":
    main()
