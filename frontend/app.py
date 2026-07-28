import sys
from pathlib import Path

# Add project root directory to sys.path so 'frontend' imports resolve properly
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
from frontend.utils.session import init_session_state, is_authenticated, logout_user
from frontend.utils.styles import inject_custom_css
from frontend.components.auth import render_auth_page
from frontend.components.dashboard import render_dashboard_page
from frontend.components.resume_upload import render_resume_upload_page
from frontend.components.interview_setup import render_interview_setup_page
from frontend.components.interview_room import render_interview_room_page
from frontend.components.report_view import render_report_view_page
from frontend.components.leaderboard import render_leaderboard_page
from frontend.components.cv_interview import render_cv_interview_page
from frontend.components.recommendations import render_recommendations_page

# Configure Streamlit Page Layout
st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Page definitions ---
PAGES = {
    "Dashboard":         ("🏠", "Dashboard"),
    "Resume Upload":     ("📄", "Resume & CV"),
    "CV Interview":      ("📋", "Interview on CV"),
    "Interview Setup":   ("🎯", "Standard Interview"),
    "Interview Room":    ("🎙️", "Interview Room"),
    "Final Report":      ("📊", "Performance Report"),
    "Recommendations":   ("💡", "Recommendations"),
    "Leaderboard":       ("🏆", "Leaderboard"),
}

def render_sidebar(current_page: str, user: dict):
    """Render clean, functional sidebar navigation."""
    with st.sidebar:
        # Brand Header
        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-logo">🎙️ AI Interview</div>
            <div class="sidebar-tagline">Placement Readiness Platform</div>
        </div>
        """, unsafe_allow_html=True)

        # User Profile Strip
        if user:
            name = user.get('full_name', 'Candidate')
            email = user.get('email', '')
            st.markdown(f"""
            <div class="user-profile-strip">
                <div class="user-name-sidebar">👤 {name}</div>
                <div class="user-email-sidebar">{email}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<span class="nav-section-label">Main Menu</span>', unsafe_allow_html=True)

        # Navigation buttons
        nav_items = [
            ("Dashboard",       "🏠  Dashboard"),
            ("Resume Upload",   "📄  Resume & CV"),
        ]
        for key, label in nav_items:
            is_active = current_page == key
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{key}", type=btn_type, use_container_width=True):
                if current_page != key:
                    st.session_state.current_page = key
                    st.rerun()

        st.markdown('<span class="nav-section-label">Interview Modes</span>', unsafe_allow_html=True)

        interview_items = [
            ("CV Interview",    "📋  Interview on Your CV"),
            ("Interview Setup", "🎯  Standard Interview"),
            ("Interview Room",  "🎙️  Interview Room"),
        ]
        for key, label in interview_items:
            is_active = current_page == key
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{key}", type=btn_type, use_container_width=True):
                if current_page != key:
                    st.session_state.current_page = key
                    st.rerun()

        st.markdown('<span class="nav-section-label">Results & Insights</span>', unsafe_allow_html=True)

        result_items = [
            ("Final Report",     "📊  Performance Report"),
            ("Recommendations",  "💡  Recommendations"),
            ("Leaderboard",      "🏆  Leaderboard"),
        ]
        for key, label in result_items:
            is_active = current_page == key
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{key}", type=btn_type, use_container_width=True):
                if current_page != key:
                    st.session_state.current_page = key
                    st.rerun()

        # Theme toggle
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌙 Dark", use_container_width=True, key="theme_dark"):
                st.session_state.theme = "dark"
                st.rerun()
        with col2:
            if st.button("☀️ Light", use_container_width=True, key="theme_light"):
                st.session_state.theme = "light"
                st.rerun()

        st.markdown("")
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            logout_user()
            st.rerun()


def main():
    # Initialize session state
    init_session_state()

    # Initialize new session keys
    if "active_recommendations_interview_id" not in st.session_state:
        st.session_state.active_recommendations_interview_id = None

    # Apply CSS
    inject_custom_css(st.session_state.get("theme", "dark"))

    # Route unauthenticated users to auth page
    if not is_authenticated():
        render_auth_page()
        return

    user = st.session_state.user
    current = st.session_state.get("current_page", "Dashboard")

    # Render sidebar
    render_sidebar(current, user)

    # Render active page
    if current == "Dashboard":
        render_dashboard_page()
    elif current == "Resume Upload":
        render_resume_upload_page()
    elif current == "CV Interview":
        render_cv_interview_page()
    elif current == "Interview Setup":
        render_interview_setup_page()
    elif current == "Interview Room":
        render_interview_room_page()
    elif current == "Final Report":
        render_report_view_page()
    elif current == "Recommendations":
        render_recommendations_page()
    elif current == "Leaderboard":
        render_leaderboard_page()
    else:
        render_dashboard_page()


if __name__ == "__main__":
    main()
