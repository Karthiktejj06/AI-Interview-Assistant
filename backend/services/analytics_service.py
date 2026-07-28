import json
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.models.analytics import Analytics
from backend.models.user import User

logger = logging.getLogger(__name__)

def get_candidate_analytics(db: Session, user_id: int) -> Dict[str, Any]:
    """Retrieve aggregate candidate performance metrics and progress history."""
    analytics = db.query(Analytics).filter(Analytics.user_id == user_id).first()
    if not analytics:
        return {
            "total_interviews": 0,
            "average_score": 0.0,
            "weak_topics": [],
            "strong_topics": [],
            "progress_history": [],
            "last_updated": None
        }

    return {
        "total_interviews": analytics.total_interviews,
        "average_score": analytics.average_score,
        "weak_topics": json.loads(analytics.weak_topics or "[]"),
        "strong_topics": json.loads(analytics.strong_topics or "[]"),
        "progress_history": json.loads(analytics.progress_history or "[]"),
        "last_updated": analytics.last_updated
    }

def get_leaderboard_data(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve top performing candidates ranked by average score and completed interviews."""
    results = db.query(Analytics, User).join(User, Analytics.user_id == User.id)\
                .filter(Analytics.total_interviews > 0)\
                .order_by(desc(Analytics.average_score), desc(Analytics.total_interviews))\
                .limit(limit).all()

    leaderboard = []
    for analytics, user in results:
        leaderboard.append({
            "user_id": user.id,
            "full_name": user.full_name,
            "total_interviews": analytics.total_interviews,
            "average_score": analytics.average_score
        })

    return leaderboard
