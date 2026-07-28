import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.models.user import User
from backend.models.resume import Resume
from backend.models.interview import Interview
from backend.models.question import Question
from backend.models.answer import Answer
from backend.models.schemas import InterviewCreate
from backend.services.resume_service import get_user_resume
from backend.services.gemini_service import (
    generate_interview_question,
    generate_cv_based_question,
    evaluate_interview_answer
)

logger = logging.getLogger(__name__)

def start_new_interview(db: Session, user: User, setup: InterviewCreate) -> Dict[str, Any]:
    """
    Initialize a new interview session, retrieve candidate resume context,
    generate the first adaptive question (Q1), and persist to database.
    """
    is_cv_based = getattr(setup, 'cv_based', False)

    # Create Interview session record
    interview = Interview(
        user_id=user.id,
        company=setup.company,
        role=setup.role,
        difficulty=setup.difficulty,
        interview_type=setup.interview_type,
        total_questions=setup.total_questions,
        current_question_index=0,
        status="in_progress",
        score=0.0,
        cv_based=is_cv_based
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    # Fetch candidate resume details if available
    resume = get_user_resume(db, user.id)
    skills = json.loads(resume.parsed_skills) if (resume and resume.parsed_skills) else []
    projects = json.loads(resume.parsed_projects) if (resume and resume.parsed_projects) else []
    education = json.loads(resume.parsed_education) if (resume and resume.parsed_education) else []
    experience = json.loads(resume.parsed_experience) if (resume and resume.parsed_experience) else []

    # Generate Question 1 via Gemini LLM / Fallback
    if is_cv_based:
        q1_data = generate_cv_based_question(
            company=setup.company,
            role=setup.role,
            difficulty=setup.difficulty,
            interview_type=setup.interview_type,
            previous_questions=[],
            resume_skills=skills,
            resume_projects=projects,
            resume_education=education,
            resume_experience=experience,
            last_answer_score=None
        )
    else:
        q1_data = generate_interview_question(
            company=setup.company,
            role=setup.role,
            difficulty=setup.difficulty,
            interview_type=setup.interview_type,
            previous_questions=[],
            resume_skills=skills,
            resume_projects=projects,
            resume_education=education,
            resume_experience=experience,
            last_answer_score=None
        )

    # Save Q1 into database
    q1 = Question(
        interview_id=interview.id,
        question_number=1,
        question_text=q1_data.get("question_text", "Describe your technical experience."),
        expected_concepts=json.dumps(q1_data.get("expected_concepts", [])),
        topic=q1_data.get("topic", "General"),
        difficulty=q1_data.get("difficulty", setup.difficulty)
    )
    db.add(q1)
    
    # Update interview current_question_index to 1
    interview.current_question_index = 1
    db.commit()
    db.refresh(q1)
    db.refresh(interview)

    logger.info(f"Interview {interview.id} started for user {user.id} ({setup.company} - {setup.role})")

    return {
        "interview": interview,
        "first_question": q1
    }

def submit_question_answer(
    db: Session,
    user: User,
    interview_id: int,
    question_id: int,
    user_answer: str
) -> Dict[str, Any]:
    """
    Evaluate candidate's answer for question_id, record scores & feedback,
    and dynamically adapt: generate Q_{next} or complete interview session.
    """
    interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == user.id).first()
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview session not found.")

    if interview.status == "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This interview has already been completed.")

    question = db.query(Question).filter(Question.id == question_id, Question.interview_id == interview.id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found in this interview.")

    # Check if answer already submitted for this question
    existing_answer = db.query(Answer).filter(Answer.question_id == question.id).first()
    if existing_answer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Answer already submitted for this question.")

    expected_concepts = json.loads(question.expected_concepts or "[]")

    # Evaluate Answer via Gemini LLM
    eval_result = evaluate_interview_answer(
        company=interview.company,
        role=interview.role,
        topic=question.topic,
        question_text=question.question_text,
        expected_concepts=expected_concepts,
        user_answer=user_answer
    )

    # Save Answer Record
    answer = Answer(
        interview_id=interview.id,
        question_id=question.id,
        user_answer=user_answer,
        correctness_score=eval_result.get("correctness_score", 0.0),
        completeness_score=eval_result.get("completeness_score", 0.0),
        technical_accuracy_score=eval_result.get("technical_accuracy_score", 0.0),
        communication_score=eval_result.get("communication_score", 0.0),
        confidence_score=eval_result.get("confidence_score", 0.0),
        total_score=eval_result.get("total_score", 0.0),
        best_answer=eval_result.get("best_answer", ""),
        missing_concepts=json.dumps(eval_result.get("missing_concepts", [])),
        feedback=eval_result.get("feedback", "")
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)

    # Check progress
    current_q_num = question.question_number

    if current_q_num >= interview.total_questions:
        # Final Question Answered -> Complete Interview
        interview.status = "completed"
        interview.completed_at = datetime.now(timezone.utc)
        
        # Calculate Average Overall Score
        all_answers = db.query(Answer).filter(Answer.interview_id == interview.id).all()
        if all_answers:
            avg_score = sum(a.total_score for a in all_answers) / len(all_answers)
            interview.score = round(avg_score, 1)
        
        db.commit()
        db.refresh(interview)
        logger.info(f"Interview {interview.id} completed. Overall score: {interview.score}")

        return {
            "status": "completed",
            "evaluation": answer,
            "interview": interview,
            "next_question": None
        }
    else:
        # Generate Next Adaptive Question
        next_q_num = current_q_num + 1

        # Retrieve previous questions to avoid repetition
        prev_questions_objs = db.query(Question).filter(Question.interview_id == interview.id).all()
        prev_question_texts = [q.question_text for q in prev_questions_objs]

        # Retrieve resume details
        resume = get_user_resume(db, user.id)
        skills = json.loads(resume.parsed_skills) if (resume and resume.parsed_skills) else []
        projects = json.loads(resume.parsed_projects) if (resume and resume.parsed_projects) else []
        education = json.loads(resume.parsed_education) if (resume and resume.parsed_education) else []
        experience = json.loads(resume.parsed_experience) if (resume and resume.parsed_experience) else []

        # Call Gemini for Next Question with adaptive last_answer_score
        if interview.cv_based:
            next_q_data = generate_cv_based_question(
                company=interview.company,
                role=interview.role,
                difficulty=interview.difficulty,
                interview_type=interview.interview_type,
                previous_questions=prev_question_texts,
                resume_skills=skills,
                resume_projects=projects,
                resume_education=education,
                resume_experience=experience,
                last_answer_score=answer.total_score
            )
        else:
            next_q_data = generate_interview_question(
                company=interview.company,
                role=interview.role,
                difficulty=interview.difficulty,
                interview_type=interview.interview_type,
                previous_questions=prev_question_texts,
                resume_skills=skills,
                resume_projects=projects,
                resume_education=education,
                resume_experience=experience,
                last_answer_score=answer.total_score
            )

        next_q = Question(
            interview_id=interview.id,
            question_number=next_q_num,
            question_text=next_q_data.get("question_text", "Explain object oriented programming in Python."),
            expected_concepts=json.dumps(next_q_data.get("expected_concepts", [])),
            topic=next_q_data.get("topic", "General"),
            difficulty=next_q_data.get("difficulty", interview.difficulty)
        )
        db.add(next_q)
        interview.current_question_index = next_q_num
        db.commit()
        db.refresh(next_q)
        db.refresh(interview)

        return {
            "status": "in_progress",
            "evaluation": answer,
            "interview": interview,
            "next_question": next_q
        }

def get_interview_details(db: Session, user: User, interview_id: int) -> Dict[str, Any]:
    """Retrieve complete interview session state, questions, and answers."""
    interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == user.id).first()
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview session not found.")

    questions = db.query(Question).filter(Question.interview_id == interview.id).order_by(Question.question_number).all()
    answers = db.query(Answer).filter(Answer.interview_id == interview.id).all()
    
    # Map answers by question_id
    answers_map = {a.question_id: a for a in answers}

    questions_with_answers = []
    for q in questions:
        ans = answers_map.get(q.id)
        questions_with_answers.append({
            "question": q,
            "answer": ans
        })

    return {
        "interview": interview,
        "questions_history": questions_with_answers
    }

def list_candidate_interviews(
    db: Session,
    user_id: int,
    company: Optional[str] = None,
    role: Optional[str] = None,
    status_filter: Optional[str] = None
) -> List[Interview]:
    """List candidate's past interview sessions with optional search/filter."""
    query = db.query(Interview).filter(Interview.user_id == user_id)
    
    if company:
        query = query.filter(Interview.company.ilike(f"%{company}%"))
    if role:
        query = query.filter(Interview.role.ilike(f"%{role}%"))
    if status_filter:
        query = query.filter(Interview.status == status_filter)

    return query.order_by(Interview.created_at.desc()).all()
