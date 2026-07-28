import os
from dotenv import load_dotenv

load_dotenv()

# Backend API base URL
API_BASE_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000/api/v1")

# Supported Companies
COMPANIES = [
    "Cognizant",
    "Accenture",
    "Infosys",
    "TCS",
    "Capgemini",
    "Deloitte",
    "Wipro"
]

# Supported Roles
ROLES = [
    "Python Developer",
    "Java Developer",
    "Full Stack Developer",
    "Frontend Developer",
    "Data Analyst",
    "Data Scientist",
    "DevOps / Cloud Engineer",
    "QA / Automation Engineer",
    "HR / Behavioral"
]

# Difficulty Levels
DIFFICULTIES = ["Easy", "Medium", "Hard"]

# Interview Types
INTERVIEW_TYPES = ["Technical", "HR", "Mixed"]

# Question Counts
QUESTION_COUNTS = [5, 10, 15]
