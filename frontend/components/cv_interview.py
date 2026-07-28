import streamlit as st
from frontend.utils.api_client import get_my_resume_api, start_interview_api

def render_cv_interview_page():
    """Render the CV-Based Interview setup and launch page."""
    
    # Page Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">📋 Interview directly on your CV</div>
        <div class="page-subtitle">AI recruiter asks technical &amp; HR questions tailored to your exact resume skills, projects, and experience.</div>
    </div>
    """, unsafe_allow_html=True)

    # Check candidate resume status
    resume_data, status_code = get_my_resume_api()

    if status_code != 200 or not isinstance(resume_data, dict):
        # No resume uploaded
        st.markdown("""
        <div class="card" style="text-align: center; padding: 2.5rem 1.5rem; border: 1px dashed #F59E0B;">
            <div style="font-size: 48px; margin-bottom: 12px;">📄</div>
            <h3 style="margin-bottom: 8px; font-weight: 700;">No Resume Found</h3>
            <p style="color: #94A3B8; max-width: 500px; margin: 0 auto 1.5rem; font-size: 14px;">
                To conduct an interview tailored specifically to your background, please upload your PDF resume first. 
                Our AI will parse your skills, projects, and work experience.
            </p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("📄 Upload PDF Resume Now", type="primary", use_container_width=True, key="go_upload_cv"):
                st.session_state.current_page = "Resume Upload"
                st.rerun()
        return

    # Resume is available -> Show parsed CV details badge card
    filename = resume_data.get("filename", "Uploaded Resume")
    skills = resume_data.get("parsed_skills", [])
    projects = resume_data.get("parsed_projects", [])
    education = resume_data.get("parsed_education", [])
    experience = resume_data.get("parsed_experience", [])

    st.markdown(f"""
    <div class="cv-mode-banner">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="cv-mode-title">✓ Active Resume: {filename}</div>
            <span class="badge badge-purple">Parsed &amp; Ready</span>
        </div>
        <div style="font-size: 13px; color: #94A3B8; margin-top: 6px;">
            <b>{len(skills)}</b> skills &nbsp;•&nbsp; 
            <b>{len(projects)}</b> projects &nbsp;•&nbsp; 
            <b>{len(experience)}</b> work experiences detected
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Preview skills tag strip
    if skills:
        st.markdown('<div class="section-label">Skills Detected in Your CV</div>', unsafe_allow_html=True)
        skill_tags = "".join([f'<span class="cv-skill-tag">⚡ {s}</span>' for s in skills[:12]])
        st.markdown(f'<div style="margin-bottom: 1.25rem;">{skill_tags}</div>', unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # Interview setup form — only question type, difficulty, count
    st.markdown('<div class="section-label">Configure Your CV Interview</div>', unsafe_allow_html=True)

    with st.form(key="cv_interview_form"):
        col1, col2 = st.columns(2)

        with col1:
            interview_type = st.radio(
                "Question Type Focus",
                options=["Technical", "HR", "Mixed"],
                index=2,
                horizontal=True,
                help="Technical: Deep-dive into CV tech & projects | HR: Behavioral & background from CV | Mixed: Both"
            )

        with col2:
            c_diff, c_num = st.columns(2)
            with c_diff:
                difficulty = st.selectbox(
                    "Difficulty Level",
                    options=["Easy", "Medium", "Hard"],
                    index=1
                )
            with c_num:
                total_questions = st.selectbox(
                    "No. of Questions",
                    options=[5, 10, 15],
                    index=0
                )

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("🚀 Start Interview on My CV", type="primary", use_container_width=True)

    if submit_btn:
        with st.spinner("🤖 AI Recruiter is parsing your CV and preparing custom questions..."):
            response, status = start_interview_api(
                company="General",
                role="Based on CV",
                difficulty=difficulty,
                interview_type=interview_type,
                total_questions=total_questions,
                cv_based=True
            )

            if status == 201 and isinstance(response, dict):
                st.session_state.active_interview = response.get("interview")
                st.session_state.current_question = response.get("first_question")
                st.session_state.current_page = "Interview Room"
                st.rerun()
            else:
                err_detail = response.get("detail", "Failed to start CV interview. Please try again.") if isinstance(response, dict) else "Server error"
                st.error(f"Error: {err_detail}")
