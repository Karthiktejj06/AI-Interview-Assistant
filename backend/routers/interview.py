from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.user import User
from backend.models.schemas import (
    InterviewCreate,
    InterviewResponse,
    AnswerSubmit,
    QuestionResponse
)
from backend.services.interview_service import (
    start_new_interview,
    submit_question_answer,
    get_interview_details,
    list_candidate_interviews
)
from backend.utils.security import get_current_user

router = APIRouter(prefix="/interview", tags=["Interview Workflow"])

@router.post("/start", status_code=status.HTTP_201_CREATED)
def create_interview(
    setup: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start a new AI mock interview session and receive Question 1.
    """
    result = start_new_interview(db, current_user, setup)
    interview = result["interview"]
    first_q = result["first_question"]
    return {
        "message": "Interview session started successfully",
        "interview": InterviewResponse.model_validate(interview),
        "first_question": QuestionResponse.model_validate(first_q)
    }

@router.post("/{interview_id}/answer")
def submit_answer(
    interview_id: int,
    answer_data: AnswerSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit candidate's answer for evaluation and receive real-time feedback + next adaptive question.
    """
    result = submit_question_answer(
        db=db,
        user=current_user,
        interview_id=interview_id,
        question_id=answer_data.question_id,
        user_answer=answer_data.user_answer
    )
    
    response = {
        "status": result["status"],
        "evaluation": {
            "id": result["evaluation"].id,
            "question_id": result["evaluation"].question_id,
            "correctness_score": result["evaluation"].correctness_score,
            "completeness_score": result["evaluation"].completeness_score,
            "technical_accuracy_score": result["evaluation"].technical_accuracy_score,
            "communication_score": result["evaluation"].communication_score,
            "confidence_score": result["evaluation"].confidence_score,
            "total_score": result["evaluation"].total_score,
            "best_answer": result["evaluation"].best_answer,
            "missing_concepts": result["evaluation"].missing_concepts,
            "feedback": result["evaluation"].feedback
        },
        "interview": InterviewResponse.model_validate(result["interview"])
    }

    if result["next_question"]:
        response["next_question"] = QuestionResponse.model_validate(result["next_question"])
    else:
        response["next_question"] = None

    return response

@router.get("/history/all")
def get_interview_history(
    company: Optional[str] = Query(None, description="Filter by company"),
    role: Optional[str] = Query(None, description="Filter by role"),
    status_filter: Optional[str] = Query(None, description="Filter by status (in_progress, completed)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve candidate's previous interview history with search and filter options.
    """
    interviews = list_candidate_interviews(
        db=db,
        user_id=current_user.id,
        company=company,
        role=role,
        status_filter=status_filter
    )
    return [InterviewResponse.model_validate(i) for i in interviews]

@router.get("/{interview_id}")
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch complete interview session details, question history, and evaluations.
    """
    result = get_interview_details(db, current_user, interview_id)
    interview = result["interview"]
    history = result["questions_history"]
    
    formatted_history = []
    for item in history:
        q = item["question"]
        a = item["answer"]
        formatted_history.append({
            "question": QuestionResponse.model_validate(q),
            "answer": {
                "id": a.id,
                "user_answer": a.user_answer,
                "total_score": a.total_score,
                "feedback": a.feedback,
                "best_answer": a.best_answer,
                "evaluated_at": a.evaluated_at
            } if a else None
        })

    return {
        "interview": InterviewResponse.model_validate(interview),
        "history": formatted_history
    }
