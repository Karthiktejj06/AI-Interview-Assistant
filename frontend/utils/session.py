import streamlit as st

def init_session_state():
    """Initialize all Streamlit session state variables."""
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"
    if "active_interview" not in st.session_state:
        st.session_state.active_interview = None
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    if "last_evaluation" not in st.session_state:
        st.session_state.last_evaluation = None
    if "active_report_interview_id" not in st.session_state:
        st.session_state.active_report_interview_id = None

def is_authenticated() -> bool:
    """Check if candidate is logged in with valid token."""
    return st.session_state.get("token") is not None and st.session_state.get("user") is not None

def logout_user():
    """Clear session authentication state."""
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.active_interview = None
    st.session_state.current_question = None
    st.session_state.last_evaluation = None
    st.session_state.active_report_interview_id = None
    st.session_state.current_page = "Auth"
