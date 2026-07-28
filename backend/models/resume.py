from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.connection import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    extracted_text = Column(Text, nullable=False)
    
    # Parsed structured JSON stored as JSON string
    parsed_skills = Column(Text, nullable=True, default="[]")
    parsed_education = Column(Text, nullable=True, default="[]")
    parsed_projects = Column(Text, nullable=True, default="[]")
    parsed_experience = Column(Text, nullable=True, default="[]")

    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="resumes")

    def __repr__(self):
        return f"<Resume(id={self.id}, user_id={self.user_id}, filename='{self.filename}')>"
