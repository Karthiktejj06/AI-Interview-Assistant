from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.connection import Base

class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    total_interviews = Column(Integer, nullable=False, default=0)
    average_score = Column(Float, nullable=False, default=0.0)
    weak_topics = Column(Text, nullable=True, default="[]")  # JSON array string
    strong_topics = Column(Text, nullable=True, default="[]")  # JSON array string
    progress_history = Column(Text, nullable=True, default="[]")  # JSON array of {date, score, company, role}

    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="analytics")

    def __repr__(self):
        return f"<Analytics(id={self.id}, user_id={self.user_id}, total_interviews={self.total_interviews}, average_score={self.average_score})>"
