import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# In-memory SQLite — new connection per test via StaticPool so same DB object is shared
from sqlalchemy.pool import StaticPool

TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # Share the same in-memory connection across all threads/calls
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Import ALL ORM models so Base.metadata knows every table before create_all
import backend.database.connection as db_module
from backend.models.user import User
from backend.models.resume import Resume
from backend.models.interview import Interview
from backend.models.question import Question
from backend.models.answer import Answer
from backend.models.report import Report
from backend.models.analytics import Analytics

# Monkey-patch the app's engine and SessionLocal to use our test engine
db_module.engine = test_engine
db_module.SessionLocal = TestingSessionLocal

from backend.main import app
from backend.database.connection import Base, get_db

@pytest.fixture(scope="function")
def db():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db):
    """Provide FastAPI TestClient with overridden DB session for each test."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
