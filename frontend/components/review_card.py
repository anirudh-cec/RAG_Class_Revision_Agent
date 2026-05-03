"""Review card components for displaying upload summaries."""
import streamlit as st
from typing import List, Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.logger.custom_logger import CustomLogger

logger = CustomLogger(log_dir="logs").get_logger(__name__)


def _get_language_from_filename(filename: str) -> str:
    """Get language name from file extension."""
    ext_map = {
        '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
        '.jsx': 'JSX', '.tsx': 'TSX', '.java': 'Java', '.cpp': 'C++',
        '.c': 'C', '.go': 'Go', '.rs': 'Rust', '.rb': 'Ruby',
        '.php': 'PHP', '.sql': 'SQL', '.html': 'HTML', '.css': 'CSS',
        '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML',
        '.md': 'Markdown', '.txt': 'Text'
    }
    _, ext = os.path.splitext(filename.lower())
    return ext_map.get(ext, ext[1:].upper() if ext else 'Unknown')


def render_vtt_card(files: List[Any], on_edit: callable = None) -> None:
    """Render VTT files review card."""
    try:
        with st.container():
            st.markdown('<div class="stCard">', unsafe_allow_html=True)

            # Header
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown("### 📄 VTT Files")
            with col2:
                if on_edit:
                    if st.button("✏️ Edit", key="edit_vtt"):
                        on_edit()

            # Content
            if files:
                st.markdown(f"**{len(files)} file(s)** uploaded")

                with st.expander("View files"):
                    for f in files:
                        size = getattr(f, 'size', 0)
                        size_str = f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B"
                        st.markdown(f"- {f.name} ({size_str})")
            else:
                st.info("No VTT files uploaded")

            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error rendering VTT card: {str(e)}")
        st.error("Failed to display VTT files")


def render_code_card(files: List[Any], on_edit: callable = None) -> None:
    """Render code files review card."""
    try:
        with st.container():
            st.markdown('<div class="stCard">', unsafe_allow_html=True)

            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown("### 💻 Code Files")
            with col2:
                if on_edit:
                    if st.button("✏️ Edit", key="edit_code"):
                        on_edit()

            if files:
                # Group by language
                lang_counts = {}
                for f in files:
                    lang = _get_language_from_filename(f.name)
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1

                st.markdown(f"**{len(files)} file(s)** from **{len(lang_counts)} language(s)**")

                # Language badges
                st.markdown(
                    " ".join([f"`{lang}: {count}`" for lang, count in sorted(lang_counts.items())])
                )

                with st.expander("View files"):
                    for f in files:
                        lang = _get_language_from_filename(f.name)
                        st.markdown(f"- `{f.name}` ({lang})")
            else:
                st.info("No code files uploaded (optional)")

            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error rendering code card: {str(e)}")
        st.error("Failed to display code files")


def render_github_card(urls: List[str], branches: Dict[str, str], on_edit: callable = None) -> None:
    """Render GitHub repos review card."""
    try:
        with st.container():
            st.markdown('<div class="stCard">', unsafe_allow_html=True)

            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown("### 🐙 GitHub Repositories")
            with col2:
                if on_edit:
                    if st.button("✏️ Edit", key="edit_github"):
                        on_edit()

            if urls:
                st.markdown(f"**{len(urls)} repository(s)** will be fetched")

                for url in urls:
                    branch = branches.get(url, "main")
                    # Extract owner/repo from URL
                    parts = url.replace("https://github.com/", "").split("/")
                    if len(parts) >= 2:
                        repo_name = f"{parts[0]}/{parts[1]}"
                        st.markdown(f"- 📦 `{repo_name}` (branch: `{branch}`)")
            else:
                st.info("No GitHub repositories added (optional)")

            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error rendering GitHub card: {str(e)}")
        st.error("Failed to display GitHub repositories")
