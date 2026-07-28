def get_auth_token(client, email="candidate@test.com"):
    r = client.post("/api/v1/auth/register", json={
        "full_name": "Test Candidate",
        "email": email,
        "password": "password123"
    })
    return r.json()["access_token"]

def test_interview_workflow(client):
    """Test start interview, submit answer, and completion lifecycle."""
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Start Interview
    start_resp = client.post("/api/v1/interview/start", headers=headers, json={
        "company": "Cognizant",
        "role": "Python Developer",
        "difficulty": "Easy",
        "interview_type": "Technical",
        "total_questions": 2
    })
    assert start_resp.status_code == 201
    start_data = start_resp.json()
    interview_id = start_data["interview"]["id"]
    q1_id = start_data["first_question"]["id"]
    assert start_data["interview"]["total_questions"] == 2

    # 2. Submit Answer Q1
    ans1_resp = client.post(f"/api/v1/interview/{interview_id}/answer", headers=headers, json={
        "question_id": q1_id,
        "user_answer": "Python uses reference counting and generational garbage collection for memory management."
    })
    assert ans1_resp.status_code == 200
    ans1_data = ans1_resp.json()
    assert ans1_data["status"] == "in_progress"
    assert ans1_data["next_question"] is not None
    q2_id = ans1_data["next_question"]["id"]

    # 3. Submit Answer Q2 (Final Question)
    ans2_resp = client.post(f"/api/v1/interview/{interview_id}/answer", headers=headers, json={
        "question_id": q2_id,
        "user_answer": "Encapsulation, Abstraction, Inheritance, and Polymorphism are the key OOP pillars."
    })
    assert ans2_resp.status_code == 200
    ans2_data = ans2_resp.json()
    assert ans2_data["status"] == "completed"
    assert ans2_data["interview"]["status"] == "completed"
    assert ans2_data["next_question"] is None
