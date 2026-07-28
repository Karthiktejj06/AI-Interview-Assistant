import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.models.user import User
from backend.models.interview import Interview
from backend.models.question import Question
from backend.models.answer import Answer
from backend.models.report import Report
from backend.models.analytics import Analytics
from backend.services.gemini_service import synthesize_final_report, generate_cv_recommendations
from backend.services.resume_service import get_user_resume
from backend.utils.pdf_generator import generate_pdf_report
from backend.config import settings

logger = logging.getLogger(__name__)

def generate_report_for_interview(db: Session, user: User, interview_id: int) -> Report:
    """
    Synthesize complete performance report for an interview, create PDF document,
    save to DB, and update candidate analytics.
    """
    interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == user.id).first()
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview session not found.")

    if interview.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview is still in progress. Complete all questions before generating report."
        )

    # Check if report already exists
    existing_report = db.query(Report).filter(Report.interview_id == interview.id).first()
    if existing_report and existing_report.pdf_file_path and os.path.exists(existing_report.pdf_file_path):
        return existing_report

    # Fetch questions and answers history
    questions = db.query(Question).filter(Question.interview_id == interview.id).order_by(Question.question_number).all()
    answers = db.query(Answer).filter(Answer.interview_id == interview.id).all()
    answers_map = {a.question_id: a for a in answers}

    qa_history = []
    for q in questions:
        ans = answers_map.get(q.id)
        qa_history.append({
            "question_text": q.question_text,
            "topic": q.topic,
            "user_answer": ans.user_answer if ans else "N/A",
            "total_score": ans.total_score if ans else 0.0,
            "feedback": ans.feedback if ans else "",
            "best_answer": ans.best_answer if ans else ""
        })

    overall_score = interview.score or 0.0

    # Call Gemini synthesis / fallback generator
    synthesized = synthesize_final_report(
        company=interview.company,
        role=interview.role,
        difficulty=interview.difficulty,
        total_questions=interview.total_questions,
        overall_score=overall_score,
        qa_history=qa_history,
        candidate_name=user.full_name
    )

    pdf_filename = f"report_user_{user.id}_interview_{interview.id}.pdf"
    pdf_output_path = os.path.join(settings.UPLOAD_DIR, pdf_filename)

    scores_breakdown = {
        "Python": synthesized.get("python_score", overall_score),
        "SQL": synthesized.get("sql_score", overall_score),
        "DBMS": synthesized.get("dbms_score", overall_score),
        "OOP": synthesized.get("oop_score", overall_score),
        "Communication": synthesized.get("communication_score", overall_score)
    }

    # Generate PDF Report file
    generate_pdf_report(
        output_pdf_path=pdf_output_path,
        candidate_name=user.full_name,
        company=interview.company,
        role=interview.role,
        overall_score=overall_score,
        scores_breakdown=scores_breakdown,
        strengths=synthesized.get("strengths", []),
        weaknesses=synthesized.get("weaknesses", []),
        topics_to_improve=synthesized.get("topics_to_improve", []),
        recommended_resources=synthesized.get("recommended_resources", []),
        interview_summary=synthesized.get("interview_summary", ""),
        questions_history=[{"question": q, "answer": answers_map.get(q.id)} for q in questions]
    )

    if existing_report:
        report = existing_report
        report.overall_score = overall_score
        report.python_score = scores_breakdown["Python"]
        report.sql_score = scores_breakdown["SQL"]
        report.dbms_score = scores_breakdown["DBMS"]
        report.oop_score = scores_breakdown["OOP"]
        report.communication_score = scores_breakdown["Communication"]
        report.strengths = json.dumps(synthesized.get("strengths", []))
        report.weaknesses = json.dumps(synthesized.get("weaknesses", []))
        report.topics_to_improve = json.dumps(synthesized.get("topics_to_improve", []))
        report.recommended_resources = json.dumps(synthesized.get("recommended_resources", []))
        report.interview_summary = synthesized.get("interview_summary", "")
        report.pdf_file_path = pdf_output_path
    else:
        report = Report(
            interview_id=interview.id,
            user_id=user.id,
            overall_score=overall_score,
            python_score=scores_breakdown["Python"],
            sql_score=scores_breakdown["SQL"],
            dbms_score=scores_breakdown["DBMS"],
            oop_score=scores_breakdown["OOP"],
            communication_score=scores_breakdown["Communication"],
            strengths=json.dumps(synthesized.get("strengths", [])),
            weaknesses=json.dumps(synthesized.get("weaknesses", [])),
            topics_to_improve=json.dumps(synthesized.get("topics_to_improve", [])),
            recommended_resources=json.dumps(synthesized.get("recommended_resources", [])),
            interview_summary=synthesized.get("interview_summary", ""),
            pdf_file_path=pdf_output_path
        )
        db.add(report)

    db.commit()
    db.refresh(report)

    # Automatically update candidate Analytics table
    update_user_analytics_record(db, user.id)

    logger.info(f"Report generated successfully for interview {interview.id}")
    return report

def update_user_analytics_record(db: Session, user_id: int):
    """
    Recalculate total interviews, average score, weak/strong topics,
    and historical score progression array for candidate analytics.
    """
    analytics = db.query(Analytics).filter(Analytics.user_id == user_id).first()
    if not analytics:
        analytics = Analytics(user_id=user_id)
        db.add(analytics)

    completed_interviews = db.query(Interview).filter(
        Interview.user_id == user_id,
        Interview.status == "completed"
    ).all()

    if not completed_interviews:
        analytics.total_interviews = 0
        analytics.average_score = 0.0
        db.commit()
        return

    total_count = len(completed_interviews)
    avg_score = sum(i.score for i in completed_interviews if i.score) / total_count

    progress_history = []
    for i in completed_interviews:
        progress_history.append({
            "interview_id": i.id,
            "company": i.company,
            "role": i.role,
            "score": i.score,
            "date": i.completed_at.strftime("%Y-%m-%d") if i.completed_at else ""
        })

    # Collect reports to determine aggregate weak and strong topics
    reports = db.query(Report).filter(Report.user_id == user_id).all()
    all_weaknesses = []
    all_strengths = []
    for r in reports:
        w_list = json.loads(r.weaknesses or "[]")
        s_list = json.loads(r.strengths or "[]")
        all_weaknesses.extend(w_list)
        all_strengths.extend(s_list)

    analytics.total_interviews = total_count
    analytics.average_score = round(avg_score, 1)
    analytics.weak_topics = json.dumps(list(set(all_weaknesses))[:5])
    analytics.strong_topics = json.dumps(list(set(all_strengths))[:5])
    analytics.progress_history = json.dumps(progress_history)
    analytics.last_updated = datetime.now(timezone.utc)

    db.commit()
    db.refresh(analytics)


def get_recommendations_for_interview(db: Session, user: User, interview_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Generate personalized recommendations based on candidate's parsed resume & interview performance.
    """
    resume = get_user_resume(db, user.id)
    skills = json.loads(resume.parsed_skills) if (resume and resume.parsed_skills) else []
    projects = json.loads(resume.parsed_projects) if (resume and resume.parsed_projects) else []
    education = json.loads(resume.parsed_education) if (resume and resume.parsed_education) else []
    experience = json.loads(resume.parsed_experience) if (resume and resume.parsed_experience) else []

    target_interview = None
    if interview_id:
        target_interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == user.id).first()
    else:
        # Pick latest completed interview
        target_interview = db.query(Interview).filter(
            Interview.user_id == user.id,
            Interview.status == "completed"
        ).order_by(Interview.created_at.desc()).first()

    if target_interview:
        questions = db.query(Question).filter(Question.interview_id == target_interview.id).order_by(Question.question_number).all()
        answers = db.query(Answer).filter(Answer.interview_id == target_interview.id).all()
        answers_map = {a.question_id: a for a in answers}

        qa_history = []
        for q in questions:
            ans = answers_map.get(q.id)
            qa_history.append({
                "question_text": q.question_text,
                "topic": q.topic,
                "user_answer": ans.user_answer if ans else "N/A",
                "total_score": ans.total_score if ans else 0.0,
                "feedback": ans.feedback if ans else ""
            })

        return generate_cv_recommendations(
            company=target_interview.company,
            role=target_interview.role,
            interview_type=target_interview.interview_type,
            overall_score=target_interview.score or 0.0,
            total_questions=target_interview.total_questions,
            qa_history=qa_history,
            candidate_name=user.full_name,
            resume_skills=skills,
            resume_projects=projects,
            resume_education=education,
            resume_experience=experience
        )
    else:
        # No interview completed yet -> Generate initial CV-based recommendations
        return generate_cv_recommendations(
            company="Target Tech Companies",
            role="Software Engineer / Developer",
            interview_type="General",
            overall_score=5.0,
            total_questions=0,
            qa_history=[],
            candidate_name=user.full_name,
            resume_skills=skills,
            resume_projects=projects,
            resume_education=education,
            resume_experience=experience
        )

