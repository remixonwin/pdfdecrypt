import streamlit as st
from typing import Dict

def init_session_state(defaults: Dict) -> None:
    """Initialize session state variables"""
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value