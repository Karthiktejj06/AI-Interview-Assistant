from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.database.connection import Base

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    difficulty = Column(String(50), nullable=False, default="Medium")
    interview_type = Column(String(50), nullable=False, default="Technical")
    total_questions = Column(Integer, nullable=False, default=5)
    current_question_index = Column(Integer, nullable=False, default=0)
    status = Column(String(50), nullable=False, default="in_progress")  # in_progress, completed, abandoned
    score = Column(Float, nullable=True, default=0.0)
    cv_based = Column(Boolean, nullable=False, default=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="interviews")
    questions = relationship("Question", back_populates="interview", cascade="all, delete-orphan", order_by="Question.question_number")
    answers = relationship("Answer", back_populates="interview", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="interview", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Interview(id={self.id}, user_id={self.user_id}, company='{self.company}', role='{self.role}', status='{self.status}')>"
