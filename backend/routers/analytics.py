import json
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.user import User
from backend.models.interview import Interview
from backend.models.question import Question
from backend.models.answer import Answer
from backend.services.analytics_service import get_candidate_analytics, get_leaderboard_data
from backend.services.resume_service import get_user_resume
from backend.services.gemini_service import generate_cv_recommendations
from backend.utils.security import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics & Leaderboard"])

@router.get("/me")
def get_user_analytics_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch current user candidate dashboard analytics summary.
    """
    return get_candidate_analytics(db, current_user.id)

@router.get("/leaderboard")
def get_leaderboard(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch candidate leaderboard ranked by average interview score.
    """
    return get_leaderboard_data(db, limit=limit)

@router.get("/recommendations/{interview_id}")
def get_interview_recommendations(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate personalized career and CV improvement recommendations based on interview performance.
    """
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()
    if not interview:
        return {"error": "Interview not found"}

    questions = db.query(Question).filter(Question.interview_id == interview.id).order_by(Question.question_number).all()
    answers = db.query(Answer).filter(Answer.interview_id == interview.id).all()
    answers_map = {a.question_id: a for a in answers}

    qa_history = []
    for q in questions:
        ans = answers_map.get(q.id)
        qa_history.append({
            "question_text": q.question_text,
            "topic": q.topic,
            "user_answer": ans.user_answer if ans else "Not answered",
            "total_score": ans.total_score if ans else 0.0,
            "feedback": ans.feedback if ans else ""
        })

    resume = get_user_resume(db, current_user.id)
    skills = json.loads(resume.parsed_skills or "[]") if resume else []
    projects = json.loads(resume.parsed_projects or "[]") if resume else []
    education = json.loads(resume.parsed_education or "[]") if resume else []
    experience = json.loads(resume.parsed_experience or "[]") if resume else []

    recommendations = generate_cv_recommendations(
        company=interview.company,
        role=interview.role,
        interview_type=interview.interview_type,
        overall_score=interview.score or 0.0,
        total_questions=interview.total_questions,
        qa_history=qa_history,
        candidate_name=current_user.full_name,
        resume_skills=skills,
        resume_projects=projects,
        resume_education=education,
        resume_experience=experience
    )
    return recommendations
