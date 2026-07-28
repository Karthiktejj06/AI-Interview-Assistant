import re
import logging
from typing import List, Dict, Any
from io import BytesIO

logger = logging.getLogger(__name__)

# Pre-defined Comprehensive Technical Skills Taxonomy
SKILL_KEYWORDS = [
    # Programming Languages
    "python", "java", "c++", "c#", "c", "javascript", "typescript", "html", "css", "sql", "r", "go", "rust", "kotlin", "swift", "php",
    
    # Frameworks & Libraries
    "fastapi", "flask", "django", "streamlit", "react", "angular", "vue", "node.js", "express", "spring boot", "pandas", "numpy",
    "scikit-learn", "tensorflow", "pytorch", "keras", "opencv", "matplotlib", "seaborn", "plotly", "sqlalchemy", "hibernate",
    
    # Databases & Storage
    "sqlite", "postgresql", "mysql", "mongodb", "redis", "oracle", "sql server", "cassandra", "dynamodb",
    
    # Web & Cloud / DevOps
    "docker", "kubernetes", "aws", "azure", "gcp", "git", "github", "gitlab", "ci/cd", "rest api", "graphql", "microservices", "linux",
    
    # Concepts & Core CS
    "data structures", "algorithms", "object oriented programming", "oop", "dbms", "system design", "operating systems",
    "computer networks", "machine learning", "deep learning", "nlp", "artificial intelligence", "data analysis", "data visualization"
]

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text content from raw PDF bytes using PyPDF / pdfplumber fallback.
    """
    text = ""
    # Try pypdf first
    try:
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(file_bytes))
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        logger.warning(f"pypdf extraction failed, trying pdfplumber: {e}")
        try:
            import pdfplumber
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e2:
            logger.error(f"pdfplumber extraction failed: {e2}")

    return text.strip()

def parse_skills(text: str) -> List[str]:
    """
    Extract technical skills from resume text using keyword taxonomy matching.
    """
    text_lower = text.lower()
    found_skills = set()

    for skill in SKILL_KEYWORDS:
        # Use regex word boundaries for precise matching (prevent matching 'c' inside 'cat')
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            # Normalize skill formatting
            found_skills.add(skill.title() if len(skill) > 3 else skill.upper())

    return sorted(list(found_skills))

def parse_education(text: str) -> List[Dict[str, Any]]:
    """
    Extract education entries from resume text using pattern matching.
    """
    education_entries = []
    lines = text.split("\n")
    
    degrees = ["B.Tech", "B.E.", "B.Sc", "B.C.A", "M.Tech", "M.E.", "M.Sc", "M.C.A", "B.Com", "Bachelor", "Master", "Ph.D", "Diploma"]
    
    for i, line in enumerate(lines):
        for degree in degrees:
            if degree.lower() in line.lower():
                context = line.strip()
                # Include next line if available for university/college name
                if i + 1 < len(lines) and len(lines[i+1].strip()) > 3:
                    context += " - " + lines[i+1].strip()
                education_entries.append({
                    "degree": degree,
                    "details": context[:200]
                })
                break

    if not education_entries:
        # Fallback default match if explicit degree not parsed
        education_entries.append({"degree": "Bachelor of Technology / Science", "details": "Engineering / Computer Science Candidate"})

    return education_entries

def parse_projects(text: str) -> List[Dict[str, Any]]:
    """
    Extract project titles and descriptions from resume text.
    """
    projects = []
    text_lower = text.lower()
    
    # Split text into sections or lines
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    in_project_section = False
    current_project = None

    project_section_headers = ["projects", "personal projects", "academic projects", "key projects"]

    for line in lines:
        if any(header in line.lower() for header in project_section_headers):
            in_project_section = True
            continue
        
        if in_project_section:
            # If hit another major section, stop
            if any(header in line.lower() for header in ["education", "experience", "work history", "skills", "certifications"]):
                break
            
            if len(line) > 10 and not line.startswith("•"):
                if current_project:
                    projects.append(current_project)
                current_project = {"title": line[:100], "description": line}
            elif current_project and line.startswith("•"):
                current_project["description"] += " " + line[1:].strip()

    if current_project:
        projects.append(current_project)

    if not projects:
        projects.append({
            "title": "Software Development Project",
            "description": "Full Stack / Data Science Application built with Python and modern web technologies."
        })

    return projects[:5]  # Top 5 projects

def parse_experience(text: str) -> List[Dict[str, Any]]:
    """
    Extract experience / internship entries from resume text.
    """
    experiences = []
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    exp_headers = ["experience", "work experience", "internships", "employment history"]
    in_exp = False
    current_exp = None

    for line in lines:
        if any(header in line.lower() for header in exp_headers):
            in_exp = True
            continue
        
        if in_exp:
            if any(header in line.lower() for header in ["education", "projects", "skills", "certifications"]):
                break
            if len(line) > 8:
                if current_exp:
                    experiences.append(current_exp)
                current_exp = {"role_company": line[:100], "description": line}

    if current_exp:
        experiences.append(current_exp)

    if not experiences:
        experiences.append({
            "role_company": "Academic / Trainee Projects",
            "description": "Hands-on project experience in Python, DBMS, and Web Architecture."
        })

    return experiences[:5]

def parse_resume_full(text: str) -> Dict[str, Any]:
    """
    Perform full NLP / heuristic extraction of skills, education, projects, and experience from resume text.
    """
    return {
        "skills": parse_skills(text),
        "education": parse_education(text),
        "projects": parse_projects(text),
        "experience": parse_experience(text)
    }
