import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.models.user import User
from backend.models.analytics import Analytics
from backend.models.schemas import UserRegister, UserLogin
from backend.utils.security import get_password_hash, verify_password, create_access_token

logger = logging.getLogger(__name__)

def register_user(db: Session, user_data: UserRegister) -> dict:
    """
    Register a new candidate account, hash password, initialize analytics record,
    and return user info + JWT access token.
    """
    # Check if email is already registered
    existing_user = db.query(User).filter(User.email == user_data.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Hash the password
    hashed_pwd = get_password_hash(user_data.password)

    # Create User ORM instance
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email.lower(),
        hashed_password=hashed_pwd,
        role="candidate",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Initialize Analytics record for the candidate
    new_analytics = Analytics(
        user_id=new_user.id,
        total_interviews=0,
        average_score=0.0,
        weak_topics="[]",
        strong_topics="[]",
        progress_history="[]"
    )
    db.add(new_analytics)
    db.commit()

    # Generate JWT token
    access_token = create_access_token(subject=new_user.id)

    logger.info(f"User registered successfully: {new_user.email} (ID: {new_user.id})")

    return {
        "user": new_user,
        "access_token": access_token,
        "token_type": "bearer"
    }

def authenticate_user(db: Session, credentials: UserLogin) -> dict:
    """
    Authenticate a user by email & password and return access token.
    """
    user = db.query(User).filter(User.email == credentials.email.lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is deactivated."
        )

    access_token = create_access_token(subject=user.id)
    logger.info(f"User authenticated successfully: {user.email}")

    return {
        "user": user,
        "access_token": access_token,
        "token_type": "bearer"
    }
