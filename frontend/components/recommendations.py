import streamlit as st
from frontend.utils.api_client import (
    get_recommendations_api,
    get_interview_history_api
)

def render_recommendations_page():
    """Render personalized career recommendations derived from CV and interview performance."""
    
    # Page Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">💡 AI Career & Performance Recommendations</div>
        <div class="page-subtitle">Personalized roadmap based on your CV analysis and mock interview results.</div>
    </div>
    """, unsafe_allow_html=True)

    # Allow user to select a specific past completed interview or view latest
    interviews, status = get_interview_history_api(status_filter="completed")
    completed_interviews = interviews if (status == 200 and isinstance(interviews, list)) else []

    selected_interview_id = st.session_state.get("active_recommendations_interview_id")

    # Interview selector row
    c_sel, c_info = st.columns([2, 1])
    with c_sel:
        options = {"None": "Latest Performance & CV Profile"}
        if completed_interviews:
            for item in completed_interviews:
                options[str(item['id'])] = f"Session #{item['id']} - {item.get('company')} ({item.get('role')}) - Score: {item.get('score', 0):.1f}/10"

        # Determine index
        default_index = 0
        if selected_interview_id and str(selected_interview_id) in options:
            default_index = list(options.keys()).index(str(selected_interview_id))

        chosen_key = st.selectbox(
            "Select Interview Session to Analyze",
            options=list(options.keys()),
            format_func=lambda x: options[x],
            index=default_index,
            key="recs_interview_selector"
        )
        target_id = int(chosen_key) if chosen_key != "None" else None

    # Fetch Recommendations via API
    with st.spinner("🤖 Synthesizing personalized career recommendations..."):
        recs, rec_status = get_recommendations_api(target_id)

    if rec_status != 200 or not isinstance(recs, dict):
        st.warning("Unable to generate recommendations right now. Please complete an interview session first.")
        return

    # Extract Data
    readiness = recs.get("overall_readiness", "Almost Ready")
    readiness_score = recs.get("readiness_score", 7.0)
    cv_gaps = recs.get("cv_gaps", [])
    cv_strengths = recs.get("cv_strengths", [])
    interview_skill_gaps = recs.get("interview_skill_gaps", [])
    top_recs = recs.get("top_recommendations", [])
    learning_path = recs.get("learning_path", [])
    cv_tips = recs.get("cv_improvement_tips", [])
    next_steps = recs.get("next_steps", "")

    # ---- 1. READINESS BANNER ----
    banner_class = "readiness-ready" if readiness == "Ready" else ("readiness-almost" if readiness == "Almost Ready" else "readiness-needs")
    badge_color = "badge-green" if readiness == "Ready" else ("badge-yellow" if readiness == "Almost Ready" else "badge-red")
    
    st.markdown(f"""
    <div class="{banner_class}">
        <span class="badge {badge_color}" style="font-size: 13px; padding: 4px 14px;">Assessment Result: {readiness}</span>
        <div class="readiness-score" style="margin-top: 10px;">{readiness_score:.1f}<span style="font-size: 22px; font-weight: 500;"> / 10</span></div>
        <div style="font-weight: 600; font-size: 16px; margin-top: 4px; color: #F1F5F9;">Placement Readiness Index</div>
        <div style="font-size: 14px; max-width: 700px; margin: 10px auto 0; color: #94A3B8; line-height: 1.5;">{next_steps}</div>
    </div>
    """, unsafe_allow_html=True)

    # ---- 2. DIAGNOSTIC GRID ----
    st.markdown('<div class="section-label">CV & Interview Performance Diagnostics</div>', unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)

    with g1:
        st.markdown("""
        <div class="card" style="height: 100%;">
            <div style="font-weight: 700; font-size: 15px; color: #10B981; margin-bottom: 10px;">✨ Key Strengths Identified</div>
        """, unsafe_allow_html=True)
        if cv_strengths:
            for s in cv_strengths:
                st.markdown(f"✓ **{s}**")
        else:
            st.caption("No specific strengths logged.")
        st.markdown("</div>", unsafe_allow_html=True)

    with g2:
        st.markdown("""
        <div class="card" style="height: 100%;">
            <div style="font-weight: 700; font-size: 15px; color: #F59E0B; margin-bottom: 10px;">⚠️ CV Skill Gaps</div>
        """, unsafe_allow_html=True)
        if cv_gaps:
            for g in cv_gaps:
                st.markdown(f"• {g}")
        else:
            st.caption("No major CV gaps found.")
        st.markdown("</div>", unsafe_allow_html=True)

    with g3:
        st.markdown("""
        <div class="card" style="height: 100%;">
            <div style="font-weight: 700; font-size: 15px; color: #EF4444; margin-bottom: 10px;">🎯 Interview Topic Gaps</div>
        """, unsafe_allow_html=True)
        if interview_skill_gaps:
            for ig in interview_skill_gaps:
                st.markdown(f"• {ig}")
        else:
            st.caption("Solid interview performance overall.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ---- 3. PRIORITIZED ACTION PLAN ----
    st.markdown('<div class="section-label">Prioritized Action Plan</div>', unsafe_allow_html=True)
    
    if top_recs:
        for item in top_recs:
            priority = item.get("priority", "Medium")
            p_class = f"rec-priority-{priority.lower()}"
            p_badge = "badge-red" if priority == "High" else ("badge-yellow" if priority == "Medium" else "badge-green")
            
            st.markdown(f"""
            <div class="rec-card {p_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <div class="rec-action">{item.get('action', '')}</div>
                    <span class="badge {p_badge}">{priority} Priority</span>
                </div>
                <div class="rec-reason">{item.get('reason', '')}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ---- 4. TAILORED LEARNING PATH & CV TIPS ----
    col_path, col_tips = st.columns([3, 2])

    with col_path:
        st.markdown('<div class="section-label">Tailored Learning Roadmap</div>', unsafe_allow_html=True)
        if learning_path:
            for item in learning_path:
                topic = item.get("topic", "")
                res = item.get("resource", "")
                url = item.get("url", "#")
                time_est = item.get("estimated_time", "1-2 weeks")

                st.markdown(f"""
                <div class="learning-card">
                    <span class="learning-icon">📚</span>
                    <div style="flex-grow: 1;">
                        <div class="learning-topic">{topic}</div>
                        <div style="font-size: 12px; color: #94A3B8;">Resource: <a href="{url}" target="_blank" style="color: #60A5FA; text-decoration: underline;">{res}</a></div>
                    </div>
                    <span class="badge badge-blue">{time_est}</span>
                </div>
                """, unsafe_allow_html=True)

    with col_tips:
        st.markdown('<div class="section-label">CV Optimization Advice</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if cv_tips:
            for tip in cv_tips:
                st.markdown(f"💡 {tip}")
        else:
            st.caption("Your CV layout looks solid.")
        st.markdown("</div>", unsafe_allow_html=True)
