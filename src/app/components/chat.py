"""Chat interface component for the Streamlit app."""
import streamlit as st
from typing import List, Dict

def init_chat_state():
    """Initialize chat state if not exists."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def render_chat_interface(messages: List[Dict]):
    """Render the chat interface with message history."""
    with st.container(height=500, border=True):
        # Display chat history
        for message in messages:
            avatar = "🤖" if message["role"] == "assistant" else "😎"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

def add_message(role: str, content: str):
    """Add a message to the chat history."""
    st.session_state.messages.append({"role": role, "content": content}) 