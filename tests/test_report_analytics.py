from tests.test_interview import get_auth_token

def test_report_generation_and_analytics(client):
    """Test report synthesis, PDF generation, analytics update, and leaderboard."""
    token = get_auth_token(client, email="analytics@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Start and complete interview
    start = client.post("/api/v1/interview/start", headers=headers, json={
        "company": "TCS",
        "role": "Full Stack Developer",
        "difficulty": "Medium",
        "interview_type": "Technical",
        "total_questions": 1
    }).json()

    i_id = start["interview"]["id"]
    q_id = start["first_question"]["id"]

    client.post(f"/api/v1/interview/{i_id}/answer", headers=headers, json={
        "question_id": q_id,
        "user_answer": "REST APIs use HTTP methods like GET, POST, PUT, DELETE to communicate state between client and server."
    })

    # Generate Report
    rep_resp = client.post(f"/api/v1/report/generate/{i_id}", headers=headers)
    assert rep_resp.status_code == 200
    rep_data = rep_resp.json()["report"]
    assert "overall_score" in rep_data
    assert rep_data["pdf_file_path"] is not None

    # Fetch Analytics Dashboard
    ana_resp = client.get("/api/v1/analytics/me", headers=headers)
    assert ana_resp.status_code == 200
    ana_data = ana_resp.json()
    assert ana_data["total_interviews"] == 1

    # Fetch Leaderboard
    lead_resp = client.get("/api/v1/analytics/leaderboard", headers=headers)
    assert lead_resp.status_code == 200
    assert len(lead_resp.json()) >= 1
