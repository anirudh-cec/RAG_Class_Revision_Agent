"""Success/completion page (Step 5)."""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.logger.custom_logger import CustomLogger
from src.exception.custom_exception import RagAppException
from frontend.components.step_indicator import render_step_indicator
from frontend.utils.session_state import set_current_step, get_state, reset_session_state
from frontend.utils.file_handler import get_storage_stats


logger = CustomLogger(log_dir="logs").get_logger(__name__)


def render():
    """Render the success page."""
    try:
        logger.info("Rendering success page (Step 5)")

        # Render step indicator (all completed)
        render_step_indicator(current_step=5)

        # Success animation/header
        st.markdown("""
        <style>
        .success-container {
            text-align: center;
            padding: 2rem 0;
        }
        .success-icon {
            font-size: 5rem;
            color: #10B981;
            animation: scaleIn 0.5s ease-out;
        }
        .success-title {
            font-size: 2rem;
            font-weight: 700;
            color: #1E293B;
            margin: 1rem 0 0.5rem 0;
        }
        .success-subtitle {
            font-size: 1.125rem;
            color: #64748B;
            margin-bottom: 2rem;
        }
        @keyframes scaleIn {
            0% { transform: scale(0); opacity: 0; }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); opacity: 1; }
        }
        </style>

        <div class="success-container">
            <div class="success-icon">✅</div>
            <div class="success-title">Upload Complete!</div>
            <div class="success-subtitle">Your files have been successfully processed and saved.</div>
        </div>
        """, unsafe_allow_html=True)

        # Get upload stats
        docs_path = get_state("docs_path")
        upload_stats = get_state("upload_stats") or {}

        # Summary cards
        st.markdown("### 📊 Upload Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            vtt_files = upload_stats.get("vtt_saved", [])
            st.metric(label="VTT Files", value=len(vtt_files))

        with col2:
            code_files = upload_stats.get("code_saved", [])
            st.metric(label="Code Files", value=len(code_files))

        with col3:
            github_results = upload_stats.get("github_fetched", [])
            success_repos = sum(1 for r in github_results if r.get("success"))
            total_repos = len(github_results)
            st.metric(label="GitHub Repos", value=f"{success_repos}/{total_repos}")

        # Storage info
        if docs_path and os.path.exists(docs_path):
            try:
                stats = get_storage_stats(docs_path)
                st.markdown("---")
                st.markdown(f"📁 **Storage Location:** `{docs_path}`")
                st.markdown(f"💾 **Total Size:** {stats.get('total_size_mb', 0):.2f} MB")
                st.markdown(f"📄 **Total Files:** {stats.get('file_count', 0)}")
            except Exception as e:
                logger.warning(f"Failed to get storage stats: {str(e)}")

        # GitHub fetch details
        if github_results:
            with st.expander("GitHub Fetch Details"):
                for result in github_results:
                    url = result.get("url", "Unknown")
                    if result.get("success"):
                        st.success(f"✅ {url} - {result.get('message', 'Success')}")
                    else:
                        st.error(f"❌ {url} - {result.get('message', 'Failed')}")

        # Action buttons
        st.markdown("---")
        st.markdown("### 🚀 What's Next?")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Start New Upload", use_container_width=True):
                logger.info("Starting new upload - resetting session")
                reset_session_state()
                set_current_step(0)
                st.rerun()

        with col2:
            st.button("💬 Go to Chat", use_container_width=True, disabled=True,
                     help="Coming soon! The chat interface is under development.")

        with col3:
            if docs_path and st.button("📂 Open docs Folder", use_container_width=True):
                try:
                    import subprocess
                    if sys.platform == "darwin":  # macOS
                        subprocess.run(["open", docs_path])
                    elif sys.platform == "win32":  # Windows
                        os.startfile(docs_path)
                    else:  # Linux
                        subprocess.run(["xdg-open", docs_path])
                except Exception as e:
                    st.error(f"Could not open folder: {str(e)}")

        # Help text
        st.markdown("---")
        st.markdown("""
        💡 **What's next?** Your files are now saved and ready for RAG processing.
        You can start a new upload if you have more files, or wait for the chat interface
        to be ready.
        """)

        logger.info("Success page rendered successfully")

    except Exception as e:
        logger.error(f"Error rendering success page: {str(e)}")
        st.error("An error occurred while loading the page. Please refresh and try again.")
