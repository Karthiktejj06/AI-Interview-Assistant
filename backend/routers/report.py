import os
import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from typing import Optional
from backend.database.connection import get_db
from backend.models.user import User
from backend.models.report import Report
from backend.models.schemas import ReportResponse
from backend.services.report_service import generate_report_for_interview, get_recommendations_for_interview
from backend.utils.security import get_current_user

router = APIRouter(prefix="/report", tags=["Reports & Evaluation"])

@router.post("/generate/{interview_id}")
def generate_report(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Synthesize performance report, generate downloadable PDF, and save to database.
    """
    report = generate_report_for_interview(db, current_user, interview_id)
    return {
        "message": "Report generated successfully",
        "report": {
            "id": report.id,
            "interview_id": report.interview_id,
            "overall_score": report.overall_score,
            "python_score": report.python_score,
            "sql_score": report.sql_score,
            "dbms_score": report.dbms_score,
            "oop_score": report.oop_score,
            "communication_score": report.communication_score,
            "strengths": json.loads(report.strengths or "[]"),
            "weaknesses": json.loads(report.weaknesses or "[]"),
            "topics_to_improve": json.loads(report.topics_to_improve or "[]"),
            "recommended_resources": json.loads(report.recommended_resources or "[]"),
            "interview_summary": report.interview_summary,
            "pdf_file_path": report.pdf_file_path,
            "generated_at": report.generated_at
        }
    }

@router.get("/{interview_id}")
def get_report(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch synthesized performance report for an interview session.
    """
    report = db.query(Report).filter(Report.interview_id == interview_id, Report.user_id == current_user.id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found. Generate report first using /api/v1/report/generate/{interview_id}."
        )

    return {
        "id": report.id,
        "interview_id": report.interview_id,
        "overall_score": report.overall_score,
        "python_score": report.python_score,
        "sql_score": report.sql_score,
        "dbms_score": report.dbms_score,
        "oop_score": report.oop_score,
        "communication_score": report.communication_score,
        "strengths": json.loads(report.strengths or "[]"),
        "weaknesses": json.loads(report.weaknesses or "[]"),
        "topics_to_improve": json.loads(report.topics_to_improve or "[]"),
        "recommended_resources": json.loads(report.recommended_resources or "[]"),
        "interview_summary": report.interview_summary,
        "pdf_file_path": report.pdf_file_path,
        "generated_at": report.generated_at
    }

@router.get("/download/{interview_id}")
def download_pdf_report(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download placement-ready PDF evaluation report certificate.
    """
    report = db.query(Report).filter(Report.interview_id == interview_id, Report.user_id == current_user.id).first()
    if not report or not report.pdf_file_path or not os.path.exists(report.pdf_file_path):
        # Auto generate report if missing
        report = generate_report_for_interview(db, current_user, interview_id)

    filename = os.path.basename(report.pdf_file_path)
    return FileResponse(
        path=report.pdf_file_path,
        media_type="application/pdf",
        filename=filename
    )

@router.get("/recommendations/me")
def get_my_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized career recommendations based on active CV & latest interview performance.
    """
    return get_recommendations_for_interview(db, current_user, interview_id=None)

@router.get("/recommendations/{interview_id}")
def get_interview_recommendations(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized career recommendations for a specific interview session.
    """
    return get_recommendations_for_interview(db, current_user, interview_id=interview_id)

