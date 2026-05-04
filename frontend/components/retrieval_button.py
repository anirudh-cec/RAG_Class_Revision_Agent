"""
Retrieval Button Component

Provides a prominent button for accessing the chat interface
without requiring new ingestion.
"""

import streamlit as st
from typing import Callable, Optional


def render_retrieval_button(
    on_click: Optional[Callable] = None,
    disabled: bool = False,
    use_container_width: bool = True
) -> bool:
    """
    Render the main Retrieval button

    This button allows users to directly access the chat interface
    without ingesting new documents.
    """

    # Custom CSS for prominent button
    st.markdown("""
    <style>
    .retrieval-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        padding: 1rem 2rem;
        border-radius: 12px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .retrieval-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

    # Button with custom styling
    clicked = st.button(
        "🚀 Retrieval",
        key="retrieval_button",
        disabled=disabled,
        use_container_width=use_container_width,
        help="Start chatting with your existing knowledge base"
    )

    if clicked and on_click:
        on_click()

    return clicked


def render_ingestion_progress(
    current_step: int,
    total_steps: int,
    step_name: str,
    progress_percent: float
) -> None:
    """
    Render ingestion progress bar and status

    Args:
        current_step: Current step number (1-based)
        total_steps: Total number of steps
        step_name: Name of current step
        progress_percent: Progress percentage (0-100)
    """

    st.markdown(f"### 📊 Ingestion Progress")

    # Progress bar
    progress_bar = st.progress(int(progress_percent))

    # Progress stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Step", f"{current_step}/{total_steps}")

    with col2:
        st.metric("Progress", f"{progress_percent:.1f}%")

    with col3:
        st.metric("Status", step_name)

    # Step details
    st.info(f"🔄 Currently processing: **{step_name}**")


def auto_redirect_to_chat(delay_seconds: int = 2) -> None:
    """
    Auto-redirect to chat interface after ingestion completes

    Args:
        delay_seconds: Delay before redirect
    """
    import time

    st.success("✅ Ingestion complete! Redirecting to chat...")

    # Show countdown
    progress_text = st.empty()
    progress_bar = st.progress(0)

    for i in range(delay_seconds):
        progress_text.text(f"Redirecting in {delay_seconds - i} seconds...")
        progress_bar.progress((i + 1) / delay_seconds)
        time.sleep(1)

    # Trigger redirect via session state
    st.session_state.page = "chat"
    st.rerun()
