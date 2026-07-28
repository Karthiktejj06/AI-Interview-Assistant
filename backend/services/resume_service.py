import os
import json
import uuid
import logging
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status

from backend.config import settings
from backend.models.resume import Resume
from backend.models.user import User
from backend.utils.resume_parser import extract_text_from_pdf, parse_resume_full

logger = logging.getLogger(__name__)

def upload_and_parse_resume(db: Session, user: User, file: UploadFile) -> Resume:
    """
    Handle resume file upload, save PDF to disk, extract text & entities,
    and update or create candidate Resume record in database.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported for resume upload."
        )

    # Read file bytes
    try:
        contents = file.file.read()
    except Exception as e:
        logger.error(f"Error reading uploaded file: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded resume file."
        )

    if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    # Extract text from PDF bytes
    extracted_text = extract_text_from_pdf(contents)
    if not extracted_text or len(extracted_text.strip()) < 20:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract readable text from PDF. Please ensure PDF contains selectable text."
        )

    # Parse structured resume entities
    parsed_data = parse_resume_full(extracted_text)

    # Save PDF file to static/uploads directory
    unique_filename = f"user_{user.id}_{uuid.uuid4().hex[:8]}_{file.filename}"
    file_save_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    with open(file_save_path, "wb") as f:
        f.write(contents)

    # Check if candidate already has an existing resume
    existing_resume = db.query(Resume).filter(Resume.user_id == user.id).first()

    if existing_resume:
        # Delete old file if exists
        if os.path.exists(existing_resume.file_path):
            try:
                os.remove(existing_resume.file_path)
            except Exception as e:
                logger.warning(f"Could not delete old resume file: {e}")

        # Update existing record
        existing_resume.filename = file.filename
        existing_resume.file_path = file_save_path
        existing_resume.extracted_text = extracted_text
        existing_resume.parsed_skills = json.dumps(parsed_data["skills"])
        existing_resume.parsed_education = json.dumps(parsed_data["education"])
        existing_resume.parsed_projects = json.dumps(parsed_data["projects"])
        existing_resume.parsed_experience = json.dumps(parsed_data["experience"])
        
        db.commit()
        db.refresh(existing_resume)
        logger.info(f"Updated resume for user_id={user.id}")
        return existing_resume
    else:
        # Create new resume record
        new_resume = Resume(
            user_id=user.id,
            filename=file.filename,
            file_path=file_save_path,
            extracted_text=extracted_text,
            parsed_skills=json.dumps(parsed_data["skills"]),
            parsed_education=json.dumps(parsed_data["education"]),
            parsed_projects=json.dumps(parsed_data["projects"]),
            parsed_experience=json.dumps(parsed_data["experience"])
        )
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)
        logger.info(f"Saved new resume for user_id={user.id}")
        return new_resume

def get_user_resume(db: Session, user_id: int) -> Optional[Resume]:
    """Fetch user's active parsed resume record."""
    return db.query(Resume).filter(Resume.user_id == user_id).first()

def format_resume_response(resume: Resume) -> dict:
    """Format SQLAlchemy Resume object into JSON response dict."""
    return {
        "id": resume.id,
        "user_id": resume.user_id,
        "filename": resume.filename,
        "file_path": resume.file_path,
        "parsed_skills": json.loads(resume.parsed_skills or "[]"),
        "parsed_education": json.loads(resume.parsed_education or "[]"),
        "parsed_projects": json.loads(resume.parsed_projects or "[]"),
        "parsed_experience": json.loads(resume.parsed_experience or "[]"),
        "uploaded_at": resume.uploaded_at
    }
