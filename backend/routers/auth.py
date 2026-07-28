from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.user import User
from backend.models.schemas import UserRegister, UserLogin, UserResponse, Token
from backend.services.auth_service import register_user, authenticate_user
from backend.utils.security import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user candidate account.
    Returns user details and a valid JWT access token.
    """
    result = register_user(db, user_data)
    user = result["user"]
    return {
        "message": "User registered successfully",
        "access_token": result["access_token"],
        "token_type": result["token_type"],
        "user": UserResponse.model_validate(user)
    }

@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate candidate user credentials and return JWT token.
    """
    result = authenticate_user(db, credentials)
    user = result["user"]
    return {
        "message": "Login successful",
        "access_token": result["access_token"],
        "token_type": result["token_type"],
        "user": UserResponse.model_validate(user)
    }

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2 compatible token login handler (Swagger UI support).
    """
    credentials = UserLogin(email=form_data.username, password=form_data.password)
    result = authenticate_user(db, credentials)
    return Token(access_token=result["access_token"], token_type=result["token_type"])

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Fetch current authenticated user profile.
    """
    return current_user
