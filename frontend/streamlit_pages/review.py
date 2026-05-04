"""Review page (Step 4) for final confirmation before processing."""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.logger.custom_logger import CustomLogger
from src.exception.custom_exception import RagAppException
from frontend.components.step_indicator import render_step_indicator
from frontend.components.review_card import (
    render_vtt_card, render_code_card, render_github_card
)
from frontend.utils.session_state import (
    set_current_step, get_state, set_state, clear_errors, add_error
)
from frontend.utils.file_handler import ensure_docs_folder, cleanup_on_error
from src.ingestion.pipeline import run_vtt_chunking_pipeline
from src.ingestion.embedding_pipeline import run_embedding_pipeline


logger = CustomLogger(log_dir="logs").get_logger(__name__)


def render():
    """Render the review page."""
    try:
        logger.info("Rendering review page (Step 4)")

        # Render step indicator
        render_step_indicator(current_step=4)

        st.markdown("## 🔍 Review Your Uploads")
        st.markdown(
            "Please review your files before processing. "
            "You can go back to edit if needed."
        )

        st.markdown("---")

        # Get files from session state
        vtt_files = get_state("vtt_files") or []
        code_files = get_state("code_files") or []
        github_urls = get_state("github_urls") or []
        github_branches = get_state("github_branches") or {}

        # Summary cards
        col1, col2, col3 = st.columns(3)

        with col1:
            render_vtt_card(
                vtt_files,
                on_edit=lambda: navigate_to_step(1)
            )

        with col2:
            render_code_card(
                code_files,
                on_edit=lambda: navigate_to_step(2)
            )

        with col3:
            render_github_card(
                github_urls,
                github_branches,
                on_edit=lambda: navigate_to_step(3)
            )

        # Storage info
        st.markdown("---")
        st.info(
            "📁 All files will be saved to the `docs/` folder in your project directory. "
            "This folder will contain subfolders for VTT files, code files, and GitHub repositories."
        )

        # Navigation and action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("← Back to GitHub", use_container_width=True):
                logger.info("Going back to GitHub upload page")
                set_current_step(3)
                st.rerun()

        with col3:
            if st.button(
                "🚀 Process and Save",
                type="primary",
                use_container_width=True
            ):
                logger.info("Starting processing")
                process_and_save()

        # Show any errors
        errors = get_state("errors") or []
        if errors:
            st.markdown("---")
            st.error("⚠️ Please fix the following errors:")
            for error in errors:
                st.markdown(f"- {error}")

        logger.info("Review page rendered successfully")

    except Exception as e:
        logger.error(f"Error rendering review page: {str(e)}")
        st.error("An error occurred while loading the page. Please refresh and try again.")


def navigate_to_step(step: int):
    """Navigate to a specific step for editing."""
    logger.info(f"Navigating to step {step} for editing")
    set_current_step(step)
    st.rerun()


def process_and_save():
    """Process and save all uploaded files, then run chunking and embedding."""
    try:
        logger.info("Starting file processing")

        # Clear previous errors
        clear_errors()

        # Show progress
        progress_container = st.empty()
        with progress_container.container():
            st.markdown("### ⏳ Processing your files...")
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Get files from session state
            vtt_files = get_state("vtt_files") or []
            code_files = get_state("code_files") or []
            github_urls = get_state("github_urls") or []
            github_branches = get_state("github_branches") or {}

            # Step 1: Create docs folder structure
            status_text.markdown("📁 **Step 1/7:** Creating docs folder structure...")
            try:
                docs_path = ensure_docs_folder()
                set_state("docs_path", docs_path)
                logger.info(f"Docs folder created at: {docs_path}")
            except Exception as e:
                logger.error(f"Failed to create docs folder: {str(e)}")
                add_error(f"Failed to create docs folder: {str(e)}")
                return

            progress_bar.progress(5)

            # Step 2: Save VTT files
            status_text.markdown("📄 **Step 2/7:** Saving VTT files...")
            vtt_paths = []
            try:
                from frontend.utils.file_handler import save_vtt_files
                if vtt_files:
                    vtt_paths = save_vtt_files(vtt_files, docs_path)
                    set_state("upload_stats", {
                        **(get_state("upload_stats") or {}),
                        "vtt_saved": vtt_paths
                    })
                    logger.info(f"Saved {len(vtt_paths)} VTT files")
            except Exception as e:
                logger.error(f"Failed to save VTT files: {str(e)}")
                add_error(f"Failed to save VTT files: {str(e)}")
                return

            progress_bar.progress(15)

            # Step 3: Save code files
            status_text.markdown("💻 **Step 3/7:** Saving code files...")
            try:
                from frontend.utils.file_handler import save_code_files
                if code_files:
                    code_paths = save_code_files(code_files, docs_path)
                    set_state("upload_stats", {
                        **(get_state("upload_stats") or {}),
                        "code_saved": code_paths
                    })
                    logger.info(f"Saved {len(code_paths)} code files")
            except Exception as e:
                logger.error(f"Failed to save code files: {str(e)}")
                add_error(f"Failed to save code files: {str(e)}")
                return

            progress_bar.progress(25)

            # Step 4: Fetch GitHub repositories
            status_text.markdown("🐙 **Step 4/7:** Fetching GitHub repositories...")
            try:
                from frontend.utils.file_handler import fetch_github_repo
                if github_urls:
                    github_results = []
                    for url in github_urls:
                        branch = github_branches.get(url, "main")
                        result = fetch_github_repo(url, branch, docs_path)
                        github_results.append({
                            "url": url,
                            "branch": branch,
                            **result
                        })

                    set_state("upload_stats", {
                        **(get_state("upload_stats") or {}),
                        "github_fetched": github_results
                    })
                    logger.info(f"Fetched {len(github_results)} GitHub repositories")
            except Exception as e:
                logger.error(f"Failed to fetch GitHub repos: {str(e)}")
                add_error(f"Failed to fetch GitHub repos: {str(e)}")
                return

            progress_bar.progress(35)

            # Step 5: Chunk VTT files
            status_text.markdown("✂️ **Step 5/7:** Chunking VTT files...")
            all_chunk_paths = []
            total_chunks = 0
            try:
                for i, vtt_path in enumerate(vtt_paths):
                    chunk_output_dir = os.path.join(docs_path, "chunks", os.path.splitext(os.path.basename(vtt_path))[0])
                    status_text.markdown(f"✂️ **Step 5/7:** Chunking VTT file {i+1}/{len(vtt_paths)}...")
                    result = run_vtt_chunking_pipeline(vtt_path, output_dir=chunk_output_dir)
                    chunks_json = os.path.join(chunk_output_dir, "chunks.json")
                    all_chunk_paths.append(chunks_json)
                    total_chunks += result["validation"]["total_chunks"]
                    logger.info(f"Chunked {vtt_path}: {result['validation']['total_chunks']} chunks")

                set_state("upload_stats", {
                    **(get_state("upload_stats") or {}),
                    "chunk_paths": all_chunk_paths,
                    "total_chunks": total_chunks,
                })
            except Exception as e:
                logger.error(f"Failed to chunk VTT files: {str(e)}")
                add_error(f"VTT chunking failed: {str(e)}")
                return

            progress_bar.progress(55)

            # Step 6: Embed chunks and push to vector store
            status_text.markdown("🧠 **Step 6/7:** Embedding chunks and storing in vector DB...")
            embedding_results = []
            try:
                for i, chunks_json_path in enumerate(all_chunk_paths):
                    status_text.markdown(f"🧠 **Step 6/7:** Embedding file {i+1}/{len(all_chunk_paths)}...")
                    embed_status_path = os.path.join(
                        os.path.dirname(chunks_json_path), "..", "embedding_status.json"
                    )
                    result = run_embedding_pipeline(
                        chunks_json_path,
                        embedding_status_path=embed_status_path,
                    )
                    embedding_results.append(result)
                    logger.info(
                        f"Embedded {chunks_json_path}: "
                        f"{result['stored']}/{result['total_chunks']} stored"
                    )

                set_state("upload_stats", {
                    **(get_state("upload_stats") or {}),
                    "embedding_results": embedding_results,
                })
            except Exception as e:
                logger.error(f"Failed to embed chunks: {str(e)}")
                add_error(f"Embedding pipeline failed: {str(e)}")
                return

            progress_bar.progress(90)

            # Step 7: Finalize
            status_text.markdown("✅ **Step 7/7:** Finalizing...")

            # Clear progress UI
            progress_bar.empty()
            status_text.empty()

            # Mark as completed
            set_state("completed", True)
            set_state("processing", False)

            # Move to success page
            set_current_step(5)
            st.rerun()

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        add_error(f"An unexpected error occurred: {str(e)}")
        set_state("processing", False)
        st.rerun()
