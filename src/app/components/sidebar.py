"""Sidebar component for the Streamlit app."""
import streamlit as st
import ollama

def render_sidebar():
    """Render the sidebar with model selection and controls."""
    with st.sidebar:
        st.subheader("Model Settings")
        
        # Get available models
        try:
            models_info = ollama.list()
            available_models = tuple(model["name"] for model in models_info["models"])
            
            # Model selection
            selected_model = st.selectbox(
                "Select Model",
                available_models,
                index=0 if available_models else None,
                help="Choose a local Ollama model"
            )
            
            return selected_model
            
        except Exception as e:
            st.error(f"Error loading models: {e}")
            return None 