import time
import streamlit as st
from frontend.utils.api_client import submit_answer_api, generate_report_api

def render_interview_room_page():
    """Render Interactive Real-Time AI Interview Room."""
    interview = st.session_state.active_interview
    question = st.session_state.current_question

    if not interview or not question:
        st.warning("No active interview session found. Please setup an interview first.")
        if st.button("Go to Setup"):
            st.session_state.current_page = "Interview Setup"
            st.rerun()
        return

    company = interview["company"]
    role = interview["role"]
    total_q = interview["total_questions"]
    curr_q_num = question["question_number"]

    # Header & Progress Bar
    header_title = f"🎙️ {role} Interview Room" if company == "General" else f"🎙️ {company} • {role} Interview Room"
    st.markdown(f"## {header_title}")
    
    # Progress Calculation
    progress_val = min(1.0, curr_q_num / float(total_q))
    st.progress(progress_val, text=f"Question {curr_q_num} of {total_q} ({int(progress_val*100)}% Complete)")

    # Timer display
    t1, t2 = st.columns([3, 1])
    with t1:
        st.caption(f"Topic: **{question.get('topic', 'General')}** | Difficulty: **{question.get('difficulty', 'Medium')}**")
    with t2:
        st.info("⏱️ Active Timer: Running")

    st.markdown("<br>", unsafe_allow_html=True)

    # Question Box
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown(f"### Question {curr_q_num}")
    st.markdown(f"#### {question['question_text']}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Answer Input Box
    st.markdown("### 💬 Your Response")
    user_answer = st.text_area(
        "Type your technical response, code explanation, or solution below:",
        height=180,
        placeholder="Explain your approach, key syntax, algorithms, or design choices...",
        key=f"ans_input_{question['id']}"
    )

    col_sub, col_skip = st.columns([2, 1])
    with col_sub:
        if st.button("📤 Submit Answer for AI Evaluation", type="primary", use_container_width=True):
            if not user_answer or len(user_answer.strip()) < 5:
                st.warning("Please enter a response before submitting.")
            else:
                with st.spinner("AI Evaluator analyzing correctness, technical accuracy, completeness, and communication..."):
                    eval_data, code = submit_answer_api(
                        interview_id=interview["id"],
                        question_id=question["id"],
                        user_answer=user_answer
                    )
                    if code == 200:
                        st.session_state.last_evaluation = eval_data
                        st.session_state.active_interview = eval_data["interview"]
                        st.success("Answer evaluated!")
                        st.rerun()
                    else:
                        st.error(eval_data.get("detail", "Failed to submit answer."))

    # Display Real-time Evaluation Feedback if available
    last_eval = st.session_state.last_evaluation
    if last_eval and last_eval.get("evaluation") and last_eval["evaluation"].get("question_id") == question["id"]:
        eval_info = last_eval["evaluation"]
        next_q = last_eval.get("next_question")
        status = last_eval.get("status")

        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.markdown(f"### 📊 Answer Score: **{eval_info['total_score']} / 10.0**")

        # Metric breakdown 5 columns
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        sc1.metric("Correctness", f"{eval_info['correctness_score']:.1f}")
        sc2.metric("Completeness", f"{eval_info['completeness_score']:.1f}")
        sc3.metric("Tech Accuracy", f"{eval_info['technical_accuracy_score']:.1f}")
        sc4.metric("Communication", f"{eval_info['communication_score']:.1f}")
        sc5.metric("Confidence", f"{eval_info['confidence_score']:.1f}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 💡 AI Feedback & Insights")
        st.write(eval_info.get("feedback", ""))

        missing = eval_info.get("missing_concepts")
        if missing:
            if isinstance(missing, str):
                try:
                    import json
                    missing = json.loads(missing)
                except Exception:
                    missing = [missing]
            st.markdown("**Omitted / Missing Concepts:**")
            for m in missing:
                st.markdown(f"- ⚠️ {m}")

        best_ans = eval_info.get("best_answer")
        if best_ans:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("✨ View Ideal Model Answer (10/10 Benchmark)"):
                st.markdown(best_ans)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if status == "completed" or next_q is None:
            st.success("🎉 Interview completed! All questions answered.")
            if st.button("📊 Synthesize & View Final Report", type="primary", use_container_width=True):
                with st.spinner("Generating final candidate evaluation report and PDF certificate..."):
                    generate_report_api(interview["id"])
                    st.session_state.active_report_interview_id = interview["id"]
                    st.session_state.current_page = "Final Report"
                    st.rerun()
        else:
            if st.button("➡️ Proceed to Next Adaptive Question", type="primary", use_container_width=True):
                st.session_state.current_question = next_q
                st.session_state.last_evaluation = None
                st.rerun()
