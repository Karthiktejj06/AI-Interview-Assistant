import streamlit as st
from frontend.config import COMPANIES, ROLES, DIFFICULTIES, INTERVIEW_TYPES, QUESTION_COUNTS
from frontend.utils.api_client import start_interview_api, get_my_resume_api

def render_interview_setup_page():
    """Render Interview Setup Configuration Form."""
    st.markdown("## 🎯 Launch New AI Interview Session")
    st.markdown("<p style='color: #94A3B8;'>Configure your target enterprise, role, difficulty level, and interview focus.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Check resume status
    resume, status_code = get_my_resume_api()
    if status_code == 200:
        st.success(f"✓ Connected active resume: **{resume.get('filename')}**. Questions will align with your projects and skills.")
    else:
        st.warning("⚠️ No resume uploaded. Questions will follow standard company role benchmarks. (Upload resume for personalized questions).")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    with st.form("interview_setup_form"):
        c1, c2 = st.columns(2)
        with c1:
            company = st.selectbox("Select Target Company", options=COMPANIES, index=0)
            role = st.selectbox("Select Target Role", options=ROLES, index=0)
            difficulty = st.select_slider("Select Difficulty Level", options=DIFFICULTIES, value="Medium")

        with c2:
            interview_type = st.selectbox("Select Interview Type", options=INTERVIEW_TYPES, index=0)
            total_questions = st.radio("Number of Questions", options=QUESTION_COUNTS, index=0, horizontal=True)

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("🚀 Start Interview Session", type="primary", use_container_width=True)

        if submit_btn:
            with st.spinner(f"Initializing AI Interviewer for {company} ({role})..."):
                data, code = start_interview_api(
                    company=company,
                    role=role,
                    difficulty=difficulty,
                    interview_type=interview_type,
                    total_questions=total_questions
                )
                if code in (200, 201):
                    st.session_state.active_interview = data["interview"]
                    st.session_state.current_question = data["first_question"]
                    st.session_state.last_evaluation = None
                    st.session_state.current_page = "Interview Room"
                    st.success("Session initialized! Entering Interview Room...")
                    st.rerun()
                else:
                    st.error(data.get("detail", "Failed to start interview session."))
    st.markdown("</div>", unsafe_allow_html=True)
