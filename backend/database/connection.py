import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import settings

logger = logging.getLogger(__name__)

# Create SQLite SQLAlchemy Engine
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base for ORM Models
Base = declarative_base()

def get_db():
    """
    FastAPI dependency for database session management.
    Yields a database session and closes it after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database tables by creating all defined SQLAlchemy models.
    """
    from backend.models.user import User
    from backend.models.resume import Resume
    from backend.models.interview import Interview
    from backend.models.question import Question
    from backend.models.answer import Answer
    from backend.models.report import Report
    from backend.models.analytics import Analytics

    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
