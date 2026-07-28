import streamlit as st
import pandas as pd
from frontend.utils.api_client import get_leaderboard_api

def render_leaderboard_page():
    """Render Candidate Placement Leaderboard."""
    st.markdown("## 🏆 Candidate Placement Leaderboard")
    st.markdown("<p style='color: #94A3B8;'>Top candidates ranked by overall average interview scores and completed enterprise sessions.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    leaderboard_data, status_code = get_leaderboard_api()

    if status_code == 200 and leaderboard_data:
        df = pd.DataFrame(leaderboard_data)
        df.index = df.index + 1
        df.rename(columns={
            "full_name": "Candidate Name",
            "total_interviews": "Completed Interviews",
            "average_score": "Average Score (0-10)"
        }, inplace=True)

        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.dataframe(
            df[["Candidate Name", "Completed Interviews", "Average Score (0-10)"]],
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No candidates on leaderboard yet. Complete interview sessions to be listed!")
