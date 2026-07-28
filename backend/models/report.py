from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.connection import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    overall_score = Column(Float, nullable=False, default=0.0)
    python_score = Column(Float, nullable=False, default=0.0)
    sql_score = Column(Float, nullable=False, default=0.0)
    dbms_score = Column(Float, nullable=False, default=0.0)
    oop_score = Column(Float, nullable=False, default=0.0)
    communication_score = Column(Float, nullable=False, default=0.0)

    strengths = Column(Text, nullable=True, default="[]")  # JSON string
    weaknesses = Column(Text, nullable=True, default="[]")  # JSON string
    topics_to_improve = Column(Text, nullable=True, default="[]")  # JSON string
    recommended_resources = Column(Text, nullable=True, default="[]")  # JSON string
    interview_summary = Column(Text, nullable=True)
    pdf_file_path = Column(String(500), nullable=True)

    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    interview = relationship("Interview", back_populates="report")
    user = relationship("User", back_populates="reports")

    def __repr__(self):
        return f"<Report(id={self.id}, interview_id={self.interview_id}, overall_score={self.overall_score})>"
