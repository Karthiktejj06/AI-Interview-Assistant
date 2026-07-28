from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr, Field

# ==========================================
# AUTH & USER SCHEMAS
# ==========================================

class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# RESUME SCHEMAS
# ==========================================

class ResumeResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    file_path: str
    parsed_skills: List[str]
    parsed_education: List[Dict[str, Any]]
    parsed_projects: List[Dict[str, Any]]
    parsed_experience: List[Dict[str, Any]]
    uploaded_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# INTERVIEW SCHEMAS
# ==========================================

class InterviewCreate(BaseModel):
    company: str = Field(..., description="Target Company e.g. Cognizant, Accenture, Deloitte")
    role: str = Field(..., description="Target Role e.g. Python Developer, Data Scientist")
    difficulty: str = Field("Medium", description="Easy, Medium, Hard")
    interview_type: str = Field("Technical", description="Technical, HR, Mixed")
    total_questions: int = Field(5, description="5, 10, 15")
    cv_based: bool = Field(False, description="If True, generate questions directly from CV content")

class InterviewResponse(BaseModel):
    id: int
    user_id: int
    company: str
    role: str
    difficulty: str
    interview_type: str
    total_questions: int
    current_question_index: int
    status: str
    score: Optional[float] = 0.0
    cv_based: bool = False
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==========================================
# QUESTION SCHEMAS
# ==========================================

class QuestionResponse(BaseModel):
    id: int
    interview_id: int
    question_number: int
    question_text: str
    topic: str
    difficulty: str
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# ANSWER SCHEMAS
# ==========================================

class AnswerSubmit(BaseModel):
    question_id: int
    user_answer: str = Field(..., min_length=1)

class AnswerEvaluationResponse(BaseModel):
    id: int
    interview_id: int
    question_id: int
    user_answer: str
    correctness_score: float
    completeness_score: float
    technical_accuracy_score: float
    communication_score: float
    confidence_score: float
    total_score: float
    best_answer: str
    missing_concepts: List[str]
    feedback: str
    evaluated_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# REPORT SCHEMAS
# ==========================================

class ReportResponse(BaseModel):
    id: int
    interview_id: int
    user_id: int
    overall_score: float
    python_score: float
    sql_score: float
    dbms_score: float
    oop_score: float
    communication_score: float
    strengths: List[str]
    weaknesses: List[str]
    topics_to_improve: List[str]
    recommended_resources: List[Dict[str, str]]
    interview_summary: str
    pdf_file_path: Optional[str] = None
    generated_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# ANALYTICS SCHEMAS
# ==========================================

class AnalyticsResponse(BaseModel):
    total_interviews: int
    average_score: float
    weak_topics: List[str]
    strong_topics: List[str]
    progress_history: List[Dict[str, Any]]
    last_updated: datetime

    class Config:
        from_attributes = True

class LeaderboardEntry(BaseModel):
    user_id: int
    full_name: str
    total_interviews: int
    average_score: float
