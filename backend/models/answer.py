from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.connection import Base

class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    user_answer = Column(Text, nullable=False)
    
    # 0-10 Metrics evaluated by Gemini LLM
    correctness_score = Column(Float, nullable=False, default=0.0)
    completeness_score = Column(Float, nullable=False, default=0.0)
    technical_accuracy_score = Column(Float, nullable=False, default=0.0)
    communication_score = Column(Float, nullable=False, default=0.0)
    confidence_score = Column(Float, nullable=False, default=0.0)
    total_score = Column(Float, nullable=False, default=0.0)

    best_answer = Column(Text, nullable=True)
    missing_concepts = Column(Text, nullable=True)  # JSON or bullet list string
    feedback = Column(Text, nullable=True)

    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    interview = relationship("Interview", back_populates="answers")
    question = relationship("Question", back_populates="answer")

    def __repr__(self):
        return f"<Answer(id={self.id}, interview_id={self.interview_id}, q_id={self.question_id}, total_score={self.total_score})>"
