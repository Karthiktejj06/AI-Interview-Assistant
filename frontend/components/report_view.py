import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from frontend.utils.api_client import (
    get_report_api,
    generate_report_api,
    download_pdf_report_api,
    get_interview_details_api
)

def render_report_view_page():
    """Render Final Evaluation Report & Analytics Charts with PDF Download."""
    interview_id = st.session_state.active_report_interview_id

    if not interview_id:
        st.warning("No interview report selected. Please select an interview from your Dashboard.")
        if st.button("Go to Dashboard"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        return

    # Fetch report data
    report_data, status_code = get_report_api(interview_id)
    if status_code != 200:
        with st.spinner("Synthesizing final evaluation report..."):
            report_data, status_code = generate_report_api(interview_id)

    if status_code != 200:
        st.error("Failed to generate or fetch report.")
        return

    rep = report_data.get("report", report_data)
    interview_details, _ = get_interview_details_api(interview_id)
    interview_obj = interview_details.get("interview", {})

    company = interview_obj.get("company", "Enterprise")
    role = interview_obj.get("role", "Developer")
    overall = rep.get("overall_score", 0.0)

    # Header & Download PDF Button
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown(f"## 🏆 Candidate Performance Report")
        st.caption(f"{company} • {role} Interview Evaluation")
    with h2:
        pdf_bytes = download_pdf_report_api(interview_id)
        if pdf_bytes:
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_bytes,
                file_name=f"Interview_Report_{company}_{role}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Overall Score Box
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    c_score, c_summary = st.columns([1, 3])
    with c_score:
        st.markdown("<div class='metric-label'>Overall Score</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-value' style='font-size: 42px;'>{overall:.1f} / 10</div>", unsafe_allow_html=True)
    with c_summary:
        st.markdown("### Executive Summary")
        st.write(rep.get("interview_summary", ""))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Analytics Charts (Bar Chart + Radar Chart)
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("### 📊 Domain Score Breakdown")
        domains_data = {
            "Domain": ["Python", "SQL", "DBMS", "OOP", "Communication"],
            "Score": [
                rep.get("python_score", 0),
                rep.get("sql_score", 0),
                rep.get("dbms_score", 0),
                rep.get("oop_score", 0),
                rep.get("communication_score", 0)
            ]
        }
        df_domain = pd.DataFrame(domains_data)
        fig_bar = px.bar(
            df_domain,
            x="Domain",
            y="Score",
            color="Score",
            range_y=[0, 10],
            color_continuous_scale="Blues",
            title="Technical Competency Ratings"
        )
        fig_bar.update_layout(template="plotly_dark" if st.session_state.theme == "dark" else "plotly_white")
        st.plotly_chart(fig_bar, use_container_width=True)

    with ch2:
        st.markdown("### 🕸️ Competency Radar Profile")
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=[
                rep.get("python_score", 0),
                rep.get("sql_score", 0),
                rep.get("dbms_score", 0),
                rep.get("oop_score", 0),
                rep.get("communication_score", 0)
            ],
            theta=["Python", "SQL", "DBMS", "OOP", "Communication"],
            fill='toself',
            line_color='#3B82F6'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=False,
            template="plotly_dark" if st.session_state.theme == "dark" else "plotly_white",
            title="Skill Hexagon Assessment"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Strengths & Weaknesses Cards
    st1, st2 = st.columns(2)
    with st1:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.markdown("### ✨ Identified Strengths")
        strengths = rep.get("strengths", [])
        for s in strengths:
            st.markdown(f"- ✅ {s}")
        st.markdown("</div>", unsafe_allow_html=True)

    with st2:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.markdown("### ⚠️ Key Gaps & Weaknesses")
        weaknesses = rep.get("weaknesses", [])
        for w in weaknesses:
            st.markdown(f"- ❌ {w}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Recommended Learning Resources
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("### 📚 Recommended Learning Resources & Action Plan")
    resources = rep.get("recommended_resources", [])
    for res in resources:
        title = res.get("title", "Learning Resource")
        url = res.get("url", "#")
        st.markdown(f"- 🔗 [{title}]({url})")
    st.markdown("</div>", unsafe_allow_html=True)
