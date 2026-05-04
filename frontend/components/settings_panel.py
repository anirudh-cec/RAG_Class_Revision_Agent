"""
Settings Panel Component

Provides UI for configuring retrieval and generation settings.
"""

import streamlit as st
from typing import Dict, Any


def render_settings_panel() -> Dict[str, Any]:
    """
    Render the settings panel with toggle options.

    Returns:
        Dictionary containing current settings
    """
    st.markdown("### ⚙️ Settings")
    st.markdown("---")

    # Initialize settings in session state if not present
    if "settings" not in st.session_state:
        st.session_state.settings = {
            "hybrid_search": True,
            "reranking": True,
            "dense_k": 50,
            "sparse_k": 50,
            "rerank_k": 20,
            "final_k": 5,
        }

    settings = st.session_state.settings

    # Hybrid Search Toggle
    st.markdown("#### 🔍 Search Mode")
    hybrid_search = st.toggle(
        "Enable Hybrid Search",
        value=settings.get("hybrid_search", True),
        help="When ON: Uses dense + sparse search with RRF fusion. "
             "When OFF: Uses only dense (semantic) search."
    )
    settings["hybrid_search"] = hybrid_search

    if hybrid_search:
        st.success("✓ Hybrid search active (Dense + Sparse + RRF)")
        col1, col2 = st.columns(2)
        with col1:
            settings["dense_k"] = st.number_input(
                "Dense candidates",
                value=settings.get("dense_k", 50),
                min_value=10, max_value=200,
                help="Number of candidates from dense search"
            )
        with col2:
            settings["sparse_k"] = st.number_input(
                "Sparse candidates",
                value=settings.get("sparse_k", 50),
                min_value=10, max_value=200,
                help="Number of candidates from sparse search"
            )
    else:
        st.info("ℹ Simple search active (Dense only)")
        settings["dense_k"] = st.number_input(
            "Candidates",
            value=settings.get("dense_k", 50),
            min_value=10, max_value=200,
            help="Number of candidates from dense search"
        )

    st.markdown("---")

    # Reranking Toggle
    st.markdown("#### 🔄 Reranking")
    reranking = st.toggle(
        "Enable Cross-Encoder Reranking",
        value=settings.get("reranking", True),
        help="When ON: Uses cross-encoder (ms-marco-MiniLM-L6-v2) to rerank results. "
             "When OFF: Returns raw search results to LLM."
    )
    settings["reranking"] = reranking

    if reranking:
        st.success("✓ Reranking active (cross-encoder/ms-marco-MiniLM-L6-v2)")
        col1, col2 = st.columns(2)
        with col1:
            settings["rerank_k"] = st.number_input(
                "Rerank candidates",
                value=settings.get("rerank_k", 20),
                min_value=5, max_value=100,
                help="Number of top candidates to rerank"
            )
        with col2:
            settings["final_k"] = st.number_input(
                "Final results",
                value=settings.get("final_k", 5),
                min_value=1, max_value=20,
                help="Number of final results to send to LLM"
            )
    else:
        st.info("ℹ Reranking disabled - raw search results sent to LLM")
        settings["final_k"] = st.number_input(
            "Final results",
            value=settings.get("final_k", 5),
            min_value=1, max_value=20,
            help="Number of results to send to LLM"
        )

    st.markdown("---")

    # Display current config summary
    with st.expander("📋 Current Configuration"):
        st.json(settings)

    return settings


def get_search_config() -> dict:
    """
    Get the current search configuration from session state.

    Returns:
        Dictionary with search settings
    """
    if "settings" not in st.session_state:
        return {
            "hybrid_search": True,
            "reranking": True,
            "dense_k": 50,
            "sparse_k": 50,
            "rerank_k": 20,
            "final_k": 5,
        }
    return st.session_state.settings
