def get_auth_headers(client, email="candidate_cv@test.com"):
    r = client.post("/api/v1/auth/register", json={
        "full_name": "CV Candidate",
        "email": email,
        "password": "password123"
    })
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_cv_based_interview_creation(client):
    """Test starting a CV-based interview session."""
    headers = get_auth_headers(client)

    resp = client.post("/api/v1/interview/start", headers=headers, json={
        "company": "TCS",
        "role": "Python Developer",
        "difficulty": "Medium",
        "interview_type": "Mixed",
        "total_questions": 3,
        "cv_based": True
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["interview"]["cv_based"] is True
    assert data["interview"]["company"] == "TCS"
    assert data["first_question"]["question_text"] is not None

def test_recommendations_endpoint(client):
    """Test recommendations endpoints (for user profile and specific interview)."""
    headers = get_auth_headers(client, email="recs_candidate@test.com")

    # 1. Test /recommendations/me when no interview completed
    r1 = client.get("/api/v1/report/recommendations/me", headers=headers)
    assert r1.status_code == 200
    data1 = r1.json()
    assert "overall_readiness" in data1
    assert "top_recommendations" in data1
    assert "learning_path" in data1

    # 2. Complete an interview and fetch interview recommendations
    start_resp = client.post("/api/v1/interview/start", headers=headers, json={
        "company": "Accenture",
        "role": "Full Stack Developer",
        "difficulty": "Easy",
        "interview_type": "Technical",
        "total_questions": 1,
        "cv_based": True
    })
    assert start_resp.status_code == 201
    start_data = start_resp.json()
    interview_id = start_data["interview"]["id"]
    q1_id = start_data["first_question"]["id"]

    # Submit answer to complete interview
    client.post(f"/api/v1/interview/{interview_id}/answer", headers=headers, json={
        "question_id": q1_id,
        "user_answer": "I developed a web application using React frontend and Python FastAPI backend."
    })

    # Fetch recommendations for interview
    r2 = client.get(f"/api/v1/report/recommendations/{interview_id}", headers=headers)
    assert r2.status_code == 200
    data2 = r2.json()
    assert "overall_readiness" in data2
    assert "cv_improvement_tips" in data2
