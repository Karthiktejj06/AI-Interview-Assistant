import streamlit as st
import pandas as pd
import plotly.express as px
from frontend.utils.api_client import (
    get_analytics_api,
    get_interview_history_api,
    get_my_resume_api
)


def render_dashboard_page():
    """Render the main Candidate Dashboard."""
    user = st.session_state.user
    user_name = user.get('full_name', 'Candidate')
    user_email = user.get('email', '')

    # ---- Welcome strip ----
    st.markdown(f"""
    <div class="welcome-strip">
        <div>
            <div class="welcome-name">👋 Welcome back, {user_name}</div>
            <div class="welcome-sub">{user_email} &nbsp;•&nbsp; AI Interview Assistant</div>
        </div>
        <div class="badge badge-blue">🟢 Platform Active</div>
    </div>
    """, unsafe_allow_html=True)

    # ---- Quick Action Cards ----
    st.markdown('<div class="section-label">Quick Actions</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("""
        <div class="action-card">
            <span class="action-icon">📋</span>
            <div class="action-title">Interview on CV</div>
            <div class="action-desc">Questions based on your own resume skills, projects & experience.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start CV Interview", key="q_cv_interview", type="primary", use_container_width=True):
            st.session_state.current_page = "CV Interview"
            st.rerun()

    with c2:
        st.markdown("""
        <div class="action-card">
            <span class="action-icon">🎯</span>
            <div class="action-title">Standard Interview</div>
            <div class="action-desc">Company-specific mock sessions for Cognizant, TCS, Accenture & more.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Setup Interview", key="q_std_interview", use_container_width=True):
            st.session_state.current_page = "Interview Setup"
            st.rerun()

    with c3:
        st.markdown("""
        <div class="action-card">
            <span class="action-icon">📄</span>
            <div class="action-title">Upload Resume</div>
            <div class="action-desc">Parse your CV to personalize questions and get CV improvement tips.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Upload PDF Resume", key="q_upload", use_container_width=True):
            st.session_state.current_page = "Resume Upload"
            st.rerun()

    with c4:
        st.markdown("""
        <div class="action-card">
            <span class="action-icon">💡</span>
            <div class="action-title">Recommendations</div>
            <div class="action-desc">Get personalized career advice based on your CV and interview results.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Recommendations", key="q_recs", use_container_width=True):
            st.session_state.current_page = "Recommendations"
            st.rerun()

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ---- Fetch Analytics ----
    analytics_data, _ = get_analytics_api()
    resume_data, resume_status = get_my_resume_api()

    analytics = analytics_data if isinstance(analytics_data, dict) else {}

    # ---- Metric Cards ----
    st.markdown('<div class="section-label">Performance Overview</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Completed Interviews</div>
            <div class="metric-value">{analytics.get('total_interviews', 0)}</div>
            <div class="metric-sub">Total sessions done</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        avg = analytics.get('average_score', 0.0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Average Score</div>
            <div class="metric-value">{avg:.1f}<span style="font-size:16px; font-weight:400;">/10</span></div>
            <div class="metric-sub">Across all interviews</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        weak_count = len(analytics.get('weak_topics', []))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Focus Areas</div>
            <div class="metric-value" style="color: #F59E0B;">{weak_count}</div>
            <div class="metric-sub">Topics to improve</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        has_resume = resume_status == 200
        label = "✓ Uploaded" if has_resume else "Not Uploaded"
        color = "#10B981" if has_resume else "#F59E0B"
        fname = resume_data.get('filename', '') if has_resume else ""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Resume Status</div>
            <div class="metric-value" style="color: {color}; font-size: 18px;">{label}</div>
            <div class="metric-sub" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{fname[:25] if fname else "Upload your CV"}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- Strengths & Weaknesses ----
    col_w, col_s = st.columns(2)
    with col_w:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**⚠️ Areas to Improve**")
        weak_topics = analytics.get("weak_topics", [])
        if weak_topics:
            badges = "".join([f'<span class="badge badge-red">{t}</span>' for t in weak_topics])
            st.markdown(badges, unsafe_allow_html=True)
        else:
            st.caption("Complete an interview to identify weak areas.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_s:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**✨ Strengths**")
        strong_topics = analytics.get("strong_topics", [])
        if strong_topics:
            badges = "".join([f'<span class="badge badge-green">{t}</span>' for t in strong_topics])
            st.markdown(badges, unsafe_allow_html=True)
        else:
            st.caption("Complete an interview to see your strengths.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Progress Chart ----
    history = analytics.get("progress_history", [])
    if history:
        st.markdown('<div class="section-label" style="margin-top:1rem;">Performance Trend</div>', unsafe_allow_html=True)
        df = pd.DataFrame(history)
        if "score" in df.columns and "date" in df.columns:
            fig = px.line(
                df, x="date", y="score", markers=True,
                labels={"date": "Date", "score": "Score (0–10)"},
                color_discrete_sequence=["#3B82F6"]
            )
            fig.update_traces(line_width=2.5, marker_size=8)
            fig.update_layout(
                template="plotly_dark" if st.session_state.get("theme") == "dark" else "plotly_white",
                margin=dict(l=0, r=0, t=10, b=0),
                height=220,
                yaxis_range=[0, 10]
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ---- Interview History ----
    st.markdown('<div class="section-label">Recent Interviews</div>', unsafe_allow_html=True)

    f1, f2 = st.columns(2)
    with f1:
        search_co = st.text_input("Filter by Company", placeholder="e.g. Cognizant", key="dash_filter_co", label_visibility="collapsed")
    with f2:
        search_ro = st.text_input("Filter by Role", placeholder="e.g. Python Developer", key="dash_filter_ro", label_visibility="collapsed")

    interviews_data, status_code = get_interview_history_api(
        company=search_co or None,
        role=search_ro or None
    )

    if status_code == 200 and isinstance(interviews_data, list) and interviews_data:
        for item in interviews_data[:10]:
            score = item.get('score') or 0.0
            status = item.get('status', 'in_progress')
            cv_based = item.get('cv_based', False)
            status_class = "status-completed" if status == "completed" else "status-in_progress"
            status_label = "✓ Completed" if status == "completed" else "⏳ In Progress"
            cv_label = ' &nbsp;<span class="badge badge-purple">CV-based</span>' if cv_based else ""

            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            with col1:
                st.markdown(f"""
                <div class="card" style="margin-bottom:6px; padding: 0.85rem 1rem;">
                    <div style="font-weight:600; font-size:14px;">{item.get('company', '')} {cv_label}</div>
                    <div style="font-size:12px; color:#94A3B8;">{item.get('role', '')} &nbsp;•&nbsp; {item.get('interview_type', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                diff = item.get('difficulty', 'Medium')
                diff_color = {"Easy": "#10B981", "Medium": "#F59E0B", "Hard": "#EF4444"}.get(diff, "#94A3B8")
                st.markdown(f"""
                <div class="card" style="margin-bottom:6px; padding: 0.85rem 1rem; text-align:center;">
                    <div style="font-size:12px; color:#94A3B8;">Difficulty</div>
                    <div style="font-weight:600; color:{diff_color};">{diff}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                score_color = "#10B981" if score >= 7 else ("#F59E0B" if score >= 5 else "#EF4444")
                st.markdown(f"""
                <div class="card" style="margin-bottom:6px; padding: 0.85rem 1rem; text-align:center;">
                    <div style="font-size:12px; color:#94A3B8;">Score</div>
                    <div style="font-weight:700; font-size:16px; color:{score_color};">{score:.1f}/10</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                if status == "completed":
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("📊 Report", key=f"rep_{item['id']}", use_container_width=True):
                            st.session_state.active_report_interview_id = item['id']
                            st.session_state.current_page = "Final Report"
                            st.rerun()
                    with b2:
                        if st.button("💡 Tips", key=f"rec_{item['id']}", use_container_width=True):
                            st.session_state.active_recommendations_interview_id = item['id']
                            st.session_state.current_page = "Recommendations"
                            st.rerun()
                else:
                    if st.button("▶ Resume", key=f"res_{item['id']}", use_container_width=True, type="primary"):
                        st.session_state.active_interview = item
                        st.session_state.current_page = "Interview Room"
                        st.rerun()
    else:
        st.info("No interview sessions yet. Start your first interview above! 🚀")
