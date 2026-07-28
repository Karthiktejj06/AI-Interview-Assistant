from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.connection import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    expected_concepts = Column(Text, nullable=True)  # JSON or comma-separated concepts
    topic = Column(String(100), nullable=False, default="General")  # Python, SQL, DBMS, OOP, Communication, etc.
    difficulty = Column(String(50), nullable=False, default="Medium")  # Easy, Medium, Hard
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    interview = relationship("Interview", back_populates="questions")
    answer = relationship("Answer", back_populates="question", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Question(id={self.id}, interview_id={self.interview_id}, q_num={self.question_number}, topic='{self.topic}')>"
