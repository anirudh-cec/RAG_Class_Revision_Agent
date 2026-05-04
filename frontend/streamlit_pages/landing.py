"""Landing page (Step 0) for the application."""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.logger.custom_logger import CustomLogger
from frontend.utils.session_state import set_current_step


logger = CustomLogger(log_dir="logs").get_logger(__name__)


def render():
    """Render the landing page."""
    try:
        logger.info("Rendering landing page")

        # Hero section with custom HTML/CSS
        st.markdown("""
        <style>
        .hero-container {
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
            padding: 3rem 2rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(79, 70, 229, 0.2);
        }
        .hero-title {
            color: white !important;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            margin-bottom: 0.5rem !important;
        }
        .hero-subtitle {
            color: rgba(255, 255, 255, 0.9) !important;
            font-size: 1.125rem !important;
            margin-bottom: 1.5rem !important;
        }
        .feature-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            height: 100%;
        }
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        .feature-title {
            font-weight: 600;
            font-size: 1.125rem;
            color: #1E293B;
            margin-bottom: 0.5rem;
        }
        .feature-desc {
            color: #64748B;
            font-size: 0.875rem;
        }
        </style>

        <div class="hero-container">
            <div class="hero-title">📚 Class Recording RAG</div>
            <div class="hero-subtitle">
                Upload your class recordings, code files, and GitHub repos<br>
                to build a searchable knowledge base
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Feature cards
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📄</div>
                <div class="feature-title">Upload VTT Files</div>
                <div class="feature-desc">Upload subtitle files from your class recordings for indexing</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">💻</div>
                <div class="feature-title">Add Code Files</div>
                <div class="feature-desc">Include code files discussed in your classes</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🐙</div>
                <div class="feature-title">Connect GitHub</div>
                <div class="feature-desc">Link GitHub repositories for reference</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # CTA button
        col_center = st.columns([1, 2, 1])[1]
        with col_center:
            if st.button("🚀 Get Started", key="get_started_btn", use_container_width=True):
                logger.info("Get Started clicked, moving to step 1")
                set_current_step(1)
                st.rerun()

        # Footer
        st.markdown("""
        <div style="text-align: center; margin-top: 3rem; color: #94A3B8; font-size: 0.875rem;">
            Built with ❤️ using Streamlit
        </div>
        """, unsafe_allow_html=True)

        logger.info("Landing page rendered successfully")

    except Exception as e:
        logger.error(f"Error rendering landing page: {str(e)}")
        st.error("An error occurred while loading the page. Please refresh and try again.")
