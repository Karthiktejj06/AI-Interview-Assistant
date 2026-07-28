import streamlit as st
from frontend.utils.api_client import login_user_api, register_user_api

def render_auth_page():
    """Render Login / Register tabbed interface."""
    st.markdown("<h2 style='text-align: center;'>AI Interview Assistant</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8;'>Enterprise Placement & Technical Interview Readiness Platform</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_register = st.tabs(["🔒 Candidate Login", "📝 Create Account"])

        with tab_login:
            st.markdown("### Welcome Back")
            login_email = st.text_input("Email Address", key="login_email", placeholder="candidate@example.com")
            login_password = st.text_input("Password", type="password", key="login_pass")

            if st.button("Sign In", type="primary", use_container_width=True):
                if not login_email or not login_password:
                    st.error("Please enter both email and password.")
                else:
                    with st.spinner("Authenticating..."):
                        data, status_code = login_user_api(login_email, login_password)
                        if status_code == 200:
                            st.session_state.token = data["access_token"]
                            st.session_state.user = data["user"]
                            st.session_state.current_page = "Dashboard"
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error(data.get("detail", "Invalid email or password."))

        with tab_register:
            st.markdown("### Register New Candidate")
            reg_name = st.text_input("Full Name", key="reg_name", placeholder="Yaswanth Reddy")
            reg_email = st.text_input("Email Address", key="reg_email", placeholder="candidate@example.com")
            reg_password = st.text_input("Password (min 6 chars)", type="password", key="reg_pass")

            if st.button("Create Account", type="primary", use_container_width=True):
                if not reg_name or not reg_email or not reg_password:
                    st.error("Please fill in all fields.")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    with st.spinner("Creating account..."):
                        data, status_code = register_user_api(reg_name, reg_email, reg_password)
                        if status_code in (200, 201):
                            st.session_state.token = data["access_token"]
                            st.session_state.user = data["user"]
                            st.session_state.current_page = "Dashboard"
                            st.success("Account created successfully!")
                            st.rerun()
                        else:
                            st.error(data.get("detail", "Registration failed. Try a different email."))
