"""
Chat Interface Page with Settings Panel

Claude-like chat UI with configurable retrieval settings.
"""

import streamlit as st
from typing import List, Dict, Optional
import json
import requests
from datetime import datetime

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from frontend.components.settings_panel import render_settings_panel, get_search_config


def render():
    """Render the chat interface with settings"""

    # Custom CSS for Claude-like interface
    st.markdown("""
    <style>
        .chat-container {
            max-width: 900px;
            margin: 0 auto;
        }
        .chat-message {
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        }
        .user-message {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: 15%;
        }
        .assistant-message {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            margin-right: 15%;
        }
        .source-chip {
            display: inline-flex;
            align-items: center;
            background: #e3f2fd;
            color: #1976d2;
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.75rem;
            margin-right: 0.5rem;
            margin-bottom: 0.25rem;
        }
        .settings-panel {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e9ecef;
        }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "conversation_id" not in st.session_state:
        import uuid
        st.session_state.conversation_id = str(uuid.uuid4())

    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False

    if "show_settings" not in st.session_state:
        st.session_state.show_settings = False

    # Header
    st.markdown("<h1 style='text-align: center;'>💬 Chat with Your Documents</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # Top navigation bar
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.page = "landing"
            st.session_state.current_step = 0
            st.rerun()

    with col2:
        if st.button("🆕 New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_id = str(uuid.uuid4())
            st.rerun()

    with col3:
        # Toggle settings panel
        settings_label = "⚙️ Hide Settings" if st.session_state.show_settings else "⚙️ Show Settings"
        if st.button(settings_label, use_container_width=True):
            st.session_state.show_settings = not st.session_state.show_settings
            st.rerun()

    with col4:
        # Show current mode indicator
        settings = get_search_config()
        mode_text = "🔍 Hybrid" if settings.get("hybrid_search") else "🔍 Dense"
        mode_text += " + Rerank" if settings.get("reranking") else ""
        st.info(mode_text)

    st.markdown("---")

    # Settings Panel (conditionally shown)
    if st.session_state.show_settings:
        with st.container():
            st.markdown("<div class='settings-panel'>", unsafe_allow_html=True)
            settings = render_settings_panel()
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")

    # Chat messages
    for message in st.session_state.messages:
        is_user = message["role"] == "user"
        message_class = "user-message" if is_user else "assistant-message"
        avatar = "👤" if is_user else "🤖"

        st.markdown(f"""
        <div class="chat-message {message_class}">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span>{avatar}</span>
                <strong>{"You" if is_user else "Assistant"}</strong>
            </div>
            <div>{message["content"]}</div>
        </div>
        """, unsafe_allow_html=True)

        # Render sources for assistant messages
        if not is_user and "sources" in message and message["sources"]:
            sources_html = ""
            for source in message["sources"][:5]:
                doc_name = source.get("document_id", "Unknown")[:25]
                score = source.get("reranked_score", source.get("score", 0))
                sources_html += f'<span class="source-chip">📄 {doc_name} ({score:.2f})</span>'

            st.markdown(f"""
            <div style="margin-top: 0.5rem;">
                <div style="font-size: 0.75rem; color: #6c757d; margin-bottom: 0.25rem;">Sources:</div>
                {sources_html}
            </div>
            """, unsafe_allow_html=True)

    # Thinking indicator
    if st.session_state.is_processing:
        st.markdown("""
        <div class="chat-message assistant-message">
            <div class="thinking">
                <span>Thinking...</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Input Area
    st.markdown("---")

    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])

        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Ask me anything about your documents...",
                label_visibility="collapsed",
                disabled=st.session_state.is_processing
            )

        with col2:
            submit_button = st.form_submit_button(
                "Send",
                use_container_width=True,
                disabled=st.session_state.is_processing
            )

    # Handle form submission
    if submit_button and user_input.strip():
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.messages.append(user_message)
        st.session_state.is_processing = True
        st.rerun()

    # Process assistant response
    if st.session_state.is_processing:
        last_user_message = None
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "user":
                last_user_message = msg
                break

        if last_user_message:
            try:
                # Get current settings
                settings = get_search_config()

                response = requests.post(
                    "http://localhost:8000/api/v1/chat/query",
                    json={
                        "query": last_user_message["content"],
                        "conversation_id": st.session_state.conversation_id,
                        "top_k": settings.get("final_k", 5),
                        "hybrid_search": settings.get("hybrid_search", True),
                        "reranking": settings.get("reranking", True),
                        "dense_k": settings.get("dense_k", 50),
                        "sparse_k": settings.get("sparse_k", 50),
                        "rerank_k": settings.get("rerank_k", 20),
                    },
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()
                    assistant_message = {
                        "role": "assistant",
                        "content": data["answer"],
                        "timestamp": datetime.now().isoformat(),
                        "sources": data.get("sources", [])
                    }
                    st.session_state.messages.append(assistant_message)
                else:
                    error_message = {
                        "role": "assistant",
                        "content": f"Error: {response.status_code}. Please try again.",
                        "timestamp": datetime.now().isoformat()
                    }
                    st.session_state.messages.append(error_message)

            except Exception as e:
                error_message = {
                    "role": "assistant",
                    "content": f"Error: {str(e)}. Please try again.",
                    "timestamp": datetime.now().isoformat()
                }
                st.session_state.messages.append(error_message)

        st.session_state.is_processing = False
        st.rerun()
