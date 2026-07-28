import streamlit as st
from frontend.utils.api_client import (
    upload_resume_api,
    get_my_resume_api,
    delete_resume_api
)

def render_resume_upload_page():
    """Render PDF Resume Uploader and Real-Time Parsed Profile Viewer."""
    st.markdown("## 📄 Resume Upload & Automated Parser")
    st.markdown("<p style='color: #94A3B8;'>Upload your PDF resume to generate tailored, non-repeating interview questions specific to your projects, skills, and work history.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Check if candidate already has an active uploaded resume
    existing_resume, status_code = get_my_resume_api()

    # Upload Section Card
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("### Upload PDF Resume")
    uploaded_file = st.file_uploader("Choose a PDF file (Max 10MB)", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Parse & Save Resume", type="primary"):
            with st.spinner("Extracting text and parsing technical skills, projects, and education..."):
                file_bytes = uploaded_file.read()
                data, code = upload_resume_api(file_bytes, uploaded_file.name)
                if code in (200, 201):
                    st.success("Resume uploaded and parsed successfully!")
                    st.rerun()
                else:
                    st.error(data.get("detail", "Failed to parse resume PDF."))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Display Parsed Profile if Resume exists
    if status_code == 200 and existing_resume:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        h1, h2, h3 = st.columns([3, 2, 1])
        with h1:
            st.markdown(f"### 🎯 Parsed Profile: `{existing_resume['filename']}`")
        with h2:
            if st.button("📋 Start Interview on CV", type="primary", use_container_width=True):
                st.session_state.current_page = "CV Interview"
                st.rerun()
        with h3:
            if st.button("🗑️ Delete", type="secondary", use_container_width=True):
                delete_resume_api()
                st.success("Resume removed.")
                st.rerun()

        # Parsed Technical Skills Badges
        st.markdown("#### 🛠️ Parsed Technical Skills")
        skills = existing_resume.get("parsed_skills", [])
        if skills:
            badge_html = "".join([f"<span class='badge-pill'>{s}</span>" for s in skills])
            st.markdown(badge_html, unsafe_allow_html=True)
        else:
            st.write("No explicit technical skills extracted.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Parsed Education
        st.markdown("#### 🎓 Education History")
        education = existing_resume.get("parsed_education", [])
        for edu in education:
            st.markdown(f"- **{edu.get('degree', 'Degree')}**: {edu.get('details', '')}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Parsed Key Projects
        st.markdown("#### 🚀 Key Projects")
        projects = existing_resume.get("parsed_projects", [])
        for proj in projects:
            st.markdown(f"**{proj.get('title', 'Project')}**")
            st.caption(proj.get("description", ""))

        st.markdown("<br>", unsafe_allow_html=True)

        # Parsed Work Experience / Internships
        st.markdown("#### 💼 Experience & Internships")
        experience = existing_resume.get("parsed_experience", [])
        for exp in experience:
            st.markdown(f"**{exp.get('role_company', 'Experience')}**")
            st.caption(exp.get("description", ""))

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No active resume uploaded. Upload a PDF resume above to unlock resume-driven adaptive questions.")
