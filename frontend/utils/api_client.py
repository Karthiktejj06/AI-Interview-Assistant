import requests
import streamlit as st
from typing import Dict, Any, Optional
from frontend.config import API_BASE_URL

def get_headers() -> Dict[str, str]:
    """Build Authorization headers with JWT token."""
    token = st.session_state.get("token")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

# ==========================================
# AUTH API CALLS
# ==========================================

def register_user_api(full_name: str, email: str, password: str) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/auth/register"
    payload = {"full_name": full_name, "email": email, "password": password}
    response = requests.post(url, json=payload, timeout=10)
    return response.json(), response.status_code

def login_user_api(email: str, password: str) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/auth/login"
    payload = {"email": email, "password": password}
    response = requests.post(url, json=payload, timeout=10)
    return response.json(), response.status_code

def get_me_api() -> Dict[str, Any]:
    url = f"{API_BASE_URL}/auth/me"
    response = requests.get(url, headers=get_headers(), timeout=10)
    return response.json(), response.status_code

# ==========================================
# RESUME API CALLS
# ==========================================

def upload_resume_api(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/resume/upload"
    files = {"file": (filename, file_bytes, "application/pdf")}
    response = requests.post(url, headers=get_headers(), files=files, timeout=30)
    return response.json(), response.status_code

def get_my_resume_api() -> Dict[str, Any]:
    url = f"{API_BASE_URL}/resume/me"
    response = requests.get(url, headers=get_headers(), timeout=10)
    return response.json(), response.status_code

def delete_resume_api() -> Dict[str, Any]:
    url = f"{API_BASE_URL}/resume/me"
    response = requests.delete(url, headers=get_headers(), timeout=10)
    return response.json(), response.status_code

# ==========================================
# INTERVIEW API CALLS
# ==========================================

def start_interview_api(company: str, role: str, difficulty: str, interview_type: str, total_questions: int, cv_based: bool = False) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/interview/start"
    payload = {
        "company": company,
        "role": role,
        "difficulty": difficulty,
        "interview_type": interview_type,
        "total_questions": total_questions,
        "cv_based": cv_based
    }
    response = requests.post(url, headers=get_headers(), json=payload, timeout=20)
    return response.json(), response.status_code

def submit_answer_api(interview_id: int, question_id: int, user_answer: str) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/interview/{interview_id}/answer"
    payload = {
        "question_id": question_id,
        "user_answer": user_answer
    }
    response = requests.post(url, headers=get_headers(), json=payload, timeout=30)
    return response.json(), response.status_code

def get_interview_history_api(company: Optional[str] = None, role: Optional[str] = None, status_filter: Optional[str] = None) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/interview/history/all"
    params = {}
    if company:
        params["company"] = company
    if role:
        params["role"] = role
    if status_filter:
        params["status_filter"] = status_filter
    response = requests.get(url, headers=get_headers(), params=params, timeout=10)
    return response.json(), response.status_code

def get_interview_details_api(interview_id: int) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/interview/{interview_id}"
    response = requests.get(url, headers=get_headers(), timeout=10)
    return response.json(), response.status_code

# ==========================================
# REPORT & RECOMMENDATIONS API CALLS
# ==========================================

def generate_report_api(interview_id: int) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/report/generate/{interview_id}"
    response = requests.post(url, headers=get_headers(), timeout=30)
    return response.json(), response.status_code

def get_report_api(interview_id: int) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/report/{interview_id}"
    response = requests.get(url, headers=get_headers(), timeout=10)
    return response.json(), response.status_code

def download_pdf_report_api(interview_id: int) -> bytes:
    url = f"{API_BASE_URL}/report/download/{interview_id}"
    response = requests.get(url, headers=get_headers(), timeout=30)
    if response.status_code == 200:
        return response.content
    return None

def get_recommendations_api(interview_id: Optional[int] = None) -> Dict[str, Any]:
    if interview_id:
        url = f"{API_BASE_URL}/report/recommendations/{interview_id}"
    else:
        url = f"{API_BASE_URL}/report/recommendations/me"
    response = requests.get(url, headers=get_headers(), timeout=20)
    return response.json(), response.status_code

def get_analytics_api() -> Dict[str, Any]:
    url = f"{API_BASE_URL}/analytics/me"
    response = requests.get(url, headers=get_headers(), timeout=10)
    return response.json(), response.status_code

def get_leaderboard_api() -> Dict[str, Any]:
    url = f"{API_BASE_URL}/analytics/leaderboard"
    response = requests.get(url, headers=get_headers(), timeout=10)
    return response.json(), response.status_code

