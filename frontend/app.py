"""
Main entry point for the Streamlit frontend.

Provides step-by-step ingestion flow and direct access to chat via Retrieval button.
"""

import sys
import os

# Add project root to Python path - CRITICAL for imports to work
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"DEBUG: Added {project_root} to sys.path", file=sys.stderr)

import streamlit as st

# Import pages using absolute imports from project root
try:
    from frontend.streamlit_pages import landing, vtt_upload, code_upload, github_upload, review, success
    from frontend.components import retrieval_button
    print("DEBUG: Successfully imported frontend modules", file=sys.stderr)
except ImportError as e:
    print(f"DEBUG: Import error - {e}", file=sys.stderr)
    print(f"DEBUG: sys.path = {sys.path}", file=sys.stderr)
    raise


def init_session_state():
    """Initialize session state variables"""
    if "current_step" not in st.session_state:
        st.session_state.current_step = 0

    if "vtt_files" not in st.session_state:
        st.session_state.vtt_files = []

    if "code_files" not in st.session_state:
        st.session_state.code_files = []

    if "github_urls" not in st.session_state:
        st.session_state.github_urls = []

    if "page" not in st.session_state:
        st.session_state.page = "landing"


def navigate_to_step(step: int):
    """Navigate to a specific step"""
    st.session_state.current_step = step


def navigate_to_chat():
    """Navigate to chat page"""
    st.session_state.page = "chat"
    st.rerun()


def main():
    """Main entry point"""
    st.set_page_config(
        page_title="RAG Class Assistant",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()

    # Check if we should show chat page
    if st.session_state.page == "chat":
        # Import and run chat page
        from frontend.streamlit_pages import chat
        chat.render()
        return

    # Sidebar - Show navigation and retrieval button
    with st.sidebar:
        st.title("📚 RAG Assistant")
        st.markdown("---")

        # 🚀 Retrieval Button - Direct access to chat
        st.markdown("### 🚀 Quick Access")
        if st.button(
            "💬 Go to Chat",
            use_container_width=True,
            type="primary",
            help="Start chatting with your existing knowledge base"
        ):
            navigate_to_chat()

        st.markdown("---")

        # Step indicator
        st.markdown("### 📍 Current Step")

        steps = [
            "🏠 Landing",
            "📄 Upload VTT",
            "💻 Upload Code",
            "🔗 GitHub Links",
            "✅ Review",
            "🎉 Success"
        ]

        for idx, step in enumerate(steps):
            if idx == st.session_state.current_step:
                st.markdown(f"**→ {step}**")
            else:
                st.markdown(f"  {step}")

    # Main content area
    current_step = st.session_state.current_step

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


if __name__ == "__main__":
    main()
