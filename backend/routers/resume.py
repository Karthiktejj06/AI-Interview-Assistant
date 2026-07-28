import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.user import User
from backend.models.resume import Resume
from backend.models.schemas import ResumeResponse
from backend.services.resume_service import upload_and_parse_resume, get_user_resume, format_resume_response
from backend.utils.security import get_current_user

router = APIRouter(prefix="/resume", tags=["Resume Management"])

@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload candidate PDF resume, parse skills, education, projects & experience,
    and save to database.
    """
    resume = upload_and_parse_resume(db, current_user, file)
    return {
        "message": "Resume uploaded and parsed successfully",
        "resume": format_resume_response(resume)
    }

@router.get("/me")
def get_current_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch current user's active parsed resume.
    """
    resume = get_user_resume(db, current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found for current user. Please upload a PDF resume."
        )
    return format_resume_response(resume)

@router.delete("/me")
def delete_current_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete current user's active resume.
    """
    resume = get_user_resume(db, current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found to delete."
        )

    # Remove file from disk
    if os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except Exception:
            pass

    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted successfully"}
