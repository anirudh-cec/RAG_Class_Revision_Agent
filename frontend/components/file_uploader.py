"""File uploader components for VTT and code files."""
import streamlit as st
from typing import List, Tuple, Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.logger.custom_logger import CustomLogger
from src.exception.custom_exception import RagAppException
from frontend.utils.validators import validate_vtt_file, validate_code_file


logger = CustomLogger(log_dir="logs").get_logger(__name__)


def render_vtt_uploader() -> List:
    """
    Render the VTT file uploader component.

    Returns:
        List of uploaded VTT file objects
    """
    try:
        logger.debug("Rendering VTT uploader")

        uploaded_files = st.file_uploader(
            label="Upload VTT subtitle files",
            type=["vtt"],
            accept_multiple_files=True,
            help="Upload subtitle files from your class recordings (.vtt format)",
            key="vtt_uploader"
        )

        if uploaded_files:
            logger.info(f"VTT files uploaded: {len(uploaded_files)}")

            # Validate files
            valid_files = []
            for file in uploaded_files:
                is_valid, error_msg = validate_vtt_file(file)
                if is_valid:
                    valid_files.append(file)
                else:
                    logger.warning(f"Invalid VTT file: {error_msg}")
                    st.error(f"⚠️ {error_msg}")

            # Display file list
            if valid_files:
                st.markdown("#### Uploaded Files")
                for i, file in enumerate(valid_files):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"📄 **{file.name}** ({_format_file_size(file.size)})")
                    with col2:
                        if st.button("🗑️ Remove", key=f"remove_vtt_{i}", use_container_width=True):
                            valid_files.pop(i)
                            st.rerun()

            return valid_files

        return []

    except Exception as e:
        logger.error(f"Failed to render VTT uploader: {str(e)}")
        raise RagAppException(f"Failed to render VTT uploader: {str(e)}", e)


def render_code_uploader() -> List:
    """
    Render the code file uploader component.

    Returns:
        List of uploaded code file objects
    """
    try:
        logger.debug("Rendering code uploader")

        # Define allowed extensions
        allowed_extensions = [
            "py", "js", "ts", "jsx", "tsx", "java", "cpp", "c",
            "go", "rs", "rb", "php", "sql", "html", "css", "json",
            "yaml", "yml", "md", "txt", "sh", "bat", "ps1"
        ]

        uploaded_files = st.file_uploader(
            label="Upload code files",
            type=allowed_extensions,
            accept_multiple_files=True,
            help="Upload code files discussed in your class",
            key="code_uploader"
        )

        if uploaded_files:
            logger.info(f"Code files uploaded: {len(uploaded_files)}")

            # Validate files
            valid_files = []
            for file in uploaded_files:
                is_valid, error_msg = validate_code_file(file)
                if is_valid:
                    valid_files.append(file)
                else:
                    logger.warning(f"Invalid code file: {error_msg}")
                    st.error(f"⚠️ {error_msg}")

            # Display file list with language detection
            if valid_files:
                st.markdown("#### Uploaded Files")

                # Group by language
                files_by_lang = {}
                for file in valid_files:
                    lang = _get_language_from_filename(file.name)
                    if lang not in files_by_lang:
                        files_by_lang[lang] = []
                    files_by_lang[lang].append(file)

                # Summary
                st.markdown("**Summary:** " + ", ".join([
                    f"{lang}: {len(files)}" for lang, files in files_by_lang.items()
                ]))

                # Detailed list
                for i, file in enumerate(valid_files):
                    col1, col2 = st.columns([4, 1])
                    lang = _get_language_from_filename(file.name)
                    with col1:
                        st.markdown(f"💻 **{file.name}** `{lang}` ({_format_file_size(file.size)})")
                    with col2:
                        if st.button("🗑️ Remove", key=f"remove_code_{i}", use_container_width=True):
                            valid_files.pop(i)
                            st.rerun()

            return valid_files

        return []

    except Exception as e:
        logger.error(f"Failed to render code uploader: {str(e)}")
        raise RagAppException(f"Failed to render code uploader: {str(e)}", e)


def _format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def _get_language_from_filename(filename: str) -> str:
    """Detect programming language from filename extension."""
    ext_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'React JSX',
        '.tsx': 'React TSX',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.sql': 'SQL',
        '.html': 'HTML',
        '.css': 'CSS',
        '.json': 'JSON',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.md': 'Markdown',
        '.txt': 'Text',
        '.sh': 'Shell',
        '.bat': 'Batch',
        '.ps1': 'PowerShell'
    }

    _, ext = os.path.splitext(filename.lower())
    return ext_map.get(ext, ext[1:].upper() if ext else 'Unknown')


def preview_file_content(file, max_chars: int = 500) -> Optional[str]:
    """
    Preview the content of a text file.

    Args:
        file: Uploaded file object
        max_chars: Maximum characters to preview

    Returns:
        Preview text or None if file is not text
    """
    try:
        # Reset file position
        if hasattr(file, 'seek'):
            file.seek(0)

        # Read content
        content = file.read(max_chars * 2)  # Read extra to ensure we have enough

        if hasattr(content, 'decode'):
            content = content.decode('utf-8', errors='ignore')

        # Reset file position
        if hasattr(file, 'seek'):
            file.seek(0)

        # Truncate to max_chars
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n... (truncated)"

        return content

    except Exception as e:
        logger.warning(f"Failed to preview file: {str(e)}")
        return None
