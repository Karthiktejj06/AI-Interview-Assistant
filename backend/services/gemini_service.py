import json
import re
import random
import logging
from typing import Dict, Any, List

from backend.config import settings
from backend.prompts.question_prompts import (
    QUESTION_GENERATION_PROMPT,
    ADAPTIVE_INCREASE_DIFFICULTY,
    ADAPTIVE_EASIER_FOLLOWUP,
    ADAPTIVE_NEUTRAL
)
from backend.prompts.evaluation_prompts import ANSWER_EVALUATION_PROMPT
from backend.prompts.report_prompts import FINAL_REPORT_SYNTHESIS_PROMPT
from backend.prompts.cv_interview_prompts import CV_QUESTION_GENERATION_PROMPT, CV_RECOMMENDATIONS_PROMPT

logger = logging.getLogger(__name__)

# Configure Google Generative AI SDK if key exists
gemini_initialized = False
try:
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip() != "":
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        gemini_initialized = True
        logger.info("Google Gemini API client initialized successfully.")
    else:
        logger.warning("GEMINI_API_KEY not set. Gemini service will run in intelligent mock fallback mode.")
except Exception as e:
    logger.warning(f"Could not initialize Google Gemini API SDK: {e}. Falling back to intelligent mock mode.")

def clean_json_response(raw_text: str) -> str:
    """Extract clean JSON substring from Gemini response."""
    raw_text = raw_text.strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    elif raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
    return raw_text.strip()

def call_gemini_api(prompt: str) -> str:
    """Call Google Gemini model API with prompt."""
    if not gemini_initialized:
        raise ValueError("Gemini API Key is missing or not configured.")

    import google.generativeai as genai
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text

def generate_interview_question(
    company: str,
    role: str,
    difficulty: str,
    interview_type: str,
    previous_questions: List[str],
    resume_skills: List[str],
    resume_projects: List[Dict[str, Any]],
    resume_education: List[Dict[str, Any]],
    resume_experience: List[Dict[str, Any]],
    last_answer_score: float = None
) -> Dict[str, Any]:
    """
    Generate non-repeating, resume-aligned, adaptive interview question using Gemini API.
    """
    if last_answer_score is not None:
        if last_answer_score >= 8.0:
            adaptive_instruction = ADAPTIVE_INCREASE_DIFFICULTY
        elif last_answer_score <= 4.0:
            adaptive_instruction = ADAPTIVE_EASIER_FOLLOWUP
        else:
            adaptive_instruction = ADAPTIVE_NEUTRAL
    else:
        adaptive_instruction = ADAPTIVE_NEUTRAL

    prev_q_str = "\n".join([f"- {q}" for q in previous_questions]) if previous_questions else "None"
    skills_str = ", ".join(resume_skills) if resume_skills else "Python, SQL, OOP, REST APIs"
    projects_str = ", ".join([p.get("title", "") for p in resume_projects]) if resume_projects else "Web & Data Projects"
    edu_str = ", ".join([e.get("degree", "") for e in resume_education]) if resume_education else "Computer Science Degree"
    exp_str = ", ".join([x.get("role_company", "") for x in resume_experience]) if resume_experience else "Academic Projects"

    prompt = QUESTION_GENERATION_PROMPT.format(
        company=company,
        role=role,
        difficulty=difficulty,
        interview_type=interview_type,
        previous_questions=prev_q_str,
        skills=skills_str,
        projects=projects_str,
        education=edu_str,
        experience=exp_str,
        adaptive_instruction=adaptive_instruction
    )

    if gemini_initialized:
        try:
            response_text = call_gemini_api(prompt)
            clean_text = clean_json_response(response_text)
            question_data = json.loads(clean_text)
            return question_data
        except Exception as e:
            logger.error(f"Gemini API call failed for question generation: {e}")

    # Intelligent Fallback Mock Question Generator
    return get_fallback_question(company, role, difficulty, interview_type, len(previous_questions) + 1, resume_skills, previous_questions)

COMMON_NON_TECHNICAL_WORDS = {
    "hi", "hello", "hey", "sup", "yo", "good", "fine", "ok", "okay", "k", "yes", "no",
    "test", "testing", "asdf", "qwerty", "abc", "xyz", "123", "aaa", "zzz", "foo", "bar",
    "dummy", "check", "thanks", "thank", "you", "pls", "please", "wait", "umm", "ahh",
    "lol", "haha", "whatever", "nothing", "na", "nil", "none", "help", "sorry", "bye"
}

def is_non_answer(user_answer: str) -> bool:
    """Detect if candidate gave 'I don't know', 'hi', 'test', 'no idea', 'pass', 'idk', or non-technical response."""
    if not user_answer or not user_answer.strip():
        return True
    
    text = user_answer.strip().lower()
    cleaned = re.sub(r'[^\w\s]', '', text)
    words = cleaned.split()
    
    # Single or 2-word non-technical greetings, test strings, fillers
    if len(words) <= 3:
        if all(w in COMMON_NON_TECHNICAL_WORDS or len(w) <= 2 for w in words):
            return True

    # Exact short triggers
    exact_triggers = {
        "idk", "pass", "skip", "nothing", "na", "no", "dunno", "test", "testing",
        "hi", "hello", "hey", "ok", "okay", "asdf", "qwerty", "abc", "xyz",
        "no idea", "no clue", "dont know", "don't know", "dont know the answer",
        "i dont know", "i don't know", "i dont know the answer", "i don't know the answer",
        "i have no idea", "i have no clue", "not sure", "im not sure", "i am not sure",
        "no concept", "cant answer", "can't answer", "no answer", "no experience",
        "this is a test", "hello world", "i am testing", "just testing"
    }
    if cleaned in exact_triggers:
        return True
        
    non_answer_phrases = [
        "dont know", "don't know", "do not know", "no idea", "no clue",
        "idk", "not sure", "no concept", "pass", "skip", "cant answer",
        "can't answer", "no answer", "dunno", "nothing", "na", "n/a",
        "dont have any idea", "don't have any idea", "haven't learned",
        "no experience", "no knowledge", "sorry i dont know", "sorry i don't know",
        "i dont understand", "i don't understand", "dont understand"
    ]
    
    if len(words) <= 12:
        for phrase in non_answer_phrases:
            phrase_clean = re.sub(r'[^\w\s]', '', phrase)
            if phrase_clean in cleaned:
                return True
                
    return False

def evaluate_interview_answer(
    company: str,
    role: str,
    topic: str,
    question_text: str,
    expected_concepts: List[str],
    user_answer: str
) -> Dict[str, Any]:
    """
    Evaluate candidate's answer across 5 metrics (0-10) using Gemini API.
    """
    # CRITICAL NON-ANSWER CHECK (Enforce 0.0 marks if candidate admits ignorance or types non-technical fillers)
    if is_non_answer(user_answer):
        exp_list = expected_concepts if expected_concepts else ["Core domain concepts", "Technical principles"]
        return {
            "correctness_score": 0.0,
            "completeness_score": 0.0,
            "technical_accuracy_score": 0.0,
            "communication_score": 0.0,
            "confidence_score": 0.0,
            "total_score": 0.0,
            "best_answer": f"An ideal 10/10 answer for '{question_text[:70]}...' would thoroughly explain: {', '.join(exp_list)}. Include clean syntax, architectural trade-offs, and practical examples.",
            "missing_concepts": exp_list,
            "feedback": "Your response contains no relevant technical content (e.g. greeting, test word, or admission of no answer). 0.0 marks awarded. Review the ideal response and key omitted concepts below to strengthen your understanding."
        }

    exp_concepts_str = ", ".join(expected_concepts) if expected_concepts else "Core CS Principles"
    
    prompt = ANSWER_EVALUATION_PROMPT.format(
        company=company,
        role=role,
        topic=topic,
        question_text=question_text,
        expected_concepts=exp_concepts_str,
        user_answer=user_answer
    )

    if gemini_initialized:
        try:
            response_text = call_gemini_api(prompt)
            clean_text = clean_json_response(response_text)
            eval_data = json.loads(clean_text)
            if is_non_answer(user_answer):
                eval_data["total_score"] = 0.0
                eval_data["correctness_score"] = 0.0
                eval_data["completeness_score"] = 0.0
                eval_data["technical_accuracy_score"] = 0.0
                eval_data["communication_score"] = 0.0
                eval_data["confidence_score"] = 0.0
            return eval_data
        except Exception as e:
            logger.error(f"Gemini API call failed for answer evaluation: {e}")

    # Fallback heuristic evaluation
    return get_fallback_evaluation(question_text, user_answer, expected_concepts)

def synthesize_final_report(
    company: str,
    role: str,
    difficulty: str,
    total_questions: int,
    overall_score: float,
    qa_history: List[Dict[str, Any]],
    candidate_name: str
) -> Dict[str, Any]:
    """
    Synthesize complete candidate performance evaluation report using Gemini API.
    """
    qa_summary_lines = []
    for i, qa in enumerate(qa_history, 1):
        qa_summary_lines.append(
            f"Q{i} [{qa.get('topic', 'General')}]: {qa.get('question_text')}\n"
            f"Candidate Answer: {qa.get('user_answer')}\n"
            f"Score: {qa.get('total_score', 0)}/10 | Feedback: {qa.get('feedback', '')}\n"
        )
    qa_history_str = "\n".join(qa_summary_lines)

    prompt = FINAL_REPORT_SYNTHESIS_PROMPT.format(
        company=company,
        role=role,
        difficulty=difficulty,
        total_questions=total_questions,
        overall_score=round(overall_score, 1),
        qa_history=qa_history_str,
        candidate_name=candidate_name
    )

    if gemini_initialized:
        try:
            response_text = call_gemini_api(prompt)
            clean_text = clean_json_response(response_text)
            report_data = json.loads(clean_text)
            return report_data
        except Exception as e:
            logger.error(f"Gemini API call failed for report synthesis: {e}")

    # Fallback Report Generator
    return get_fallback_report(overall_score, qa_history)

def generate_cv_based_question(
    company: str,
    role: str,
    difficulty: str,
    interview_type: str,
    previous_questions: List[str],
    resume_skills: List[str],
    resume_projects: List[Dict[str, Any]],
    resume_education: List[Dict[str, Any]],
    resume_experience: List[Dict[str, Any]],
    last_answer_score: float = None
) -> Dict[str, Any]:
    """
    Generate a question directly from the candidate's CV content using Gemini API.
    Falls back to intelligent CV-aware fallback if API unavailable.
    """
    if last_answer_score is not None:
        if last_answer_score >= 8.0:
            adaptive_instruction = ADAPTIVE_INCREASE_DIFFICULTY
        elif last_answer_score <= 4.0:
            adaptive_instruction = ADAPTIVE_EASIER_FOLLOWUP
        else:
            adaptive_instruction = ADAPTIVE_NEUTRAL
    else:
        adaptive_instruction = ADAPTIVE_NEUTRAL

    prev_q_str = "\n".join([f"- {q}" for q in previous_questions]) if previous_questions else "None"
    skills_str = ", ".join(resume_skills) if resume_skills else "General Programming"
    projects_str = "; ".join([f"{p.get('title','')}: {p.get('description','')}" for p in resume_projects]) if resume_projects else "No projects listed"
    edu_str = "; ".join([f"{e.get('degree','')} from {e.get('institution','')}" for e in resume_education]) if resume_education else "Computer Science"
    exp_str = "; ".join([f"{x.get('role_company','')}: {x.get('description','')}" for x in resume_experience]) if resume_experience else "Academic Projects"

    if gemini_initialized:
        try:
            prompt = CV_QUESTION_GENERATION_PROMPT.format(
                company=company,
                role=role,
                difficulty=difficulty,
                interview_type=interview_type,
                previous_questions=prev_q_str,
                skills=skills_str,
                projects=projects_str,
                education=edu_str,
                experience=exp_str,
                adaptive_instruction=adaptive_instruction
            )
            response_text = call_gemini_api(prompt)
            clean_text = clean_json_response(response_text)
            question_data = json.loads(clean_text)
            return question_data
        except Exception as e:
            logger.error(f"Gemini API call failed for CV question generation: {e}")

    # Intelligent fallback: build CV-specific questions from resume data
    return get_cv_fallback_question(
        role=role, difficulty=difficulty, interview_type=interview_type,
        skills=resume_skills, projects=resume_projects,
        question_num=len(previous_questions) + 1,
        previous_questions=previous_questions
    )


def generate_cv_recommendations(
    company: str,
    role: str,
    interview_type: str,
    overall_score: float,
    total_questions: int,
    qa_history: List[Dict[str, Any]],
    candidate_name: str,
    resume_skills: List[str],
    resume_projects: List[Dict[str, Any]],
    resume_education: List[Dict[str, Any]],
    resume_experience: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate personalized career recommendations based on CV content + interview performance.
    """
    skills_str = ", ".join(resume_skills) if resume_skills else "General Programming"
    projects_str = "; ".join([f"{p.get('title','')}: {p.get('description','')}" for p in resume_projects]) if resume_projects else "No projects listed"
    edu_str = "; ".join([f"{e.get('degree','')} from {e.get('institution','')}" for e in resume_education]) if resume_education else "Computer Science"
    exp_str = "; ".join([f"{x.get('role_company','')}: {x.get('description','')}" for x in resume_experience]) if resume_experience else "Academic Projects"

    qa_summary_lines = []
    for i, qa in enumerate(qa_history, 1):
        qa_summary_lines.append(
            f"Q{i} [{qa.get('topic', 'General')}]: {qa.get('question_text')}\n"
            f"Answer: {qa.get('user_answer', 'N/A')}\n"
            f"Score: {qa.get('total_score', 0)}/10\n"
        )
    qa_history_str = "\n".join(qa_summary_lines)

    if gemini_initialized:
        try:
            prompt = CV_RECOMMENDATIONS_PROMPT.format(
                candidate_name=candidate_name,
                role=role,
                company=company,
                interview_type=interview_type,
                overall_score=round(overall_score, 1),
                total_questions=total_questions,
                skills=skills_str,
                projects=projects_str,
                education=edu_str,
                experience=exp_str,
                qa_history=qa_history_str
            )
            response_text = call_gemini_api(prompt)
            clean_text = clean_json_response(response_text)
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Gemini API call failed for CV recommendations: {e}")

    return get_fallback_recommendations(overall_score, resume_skills, role, company)


def get_cv_fallback_question(
    role: str, difficulty: str, interview_type: str,
    skills: List[str], projects: List[Dict[str, Any]],
    question_num: int, previous_questions: List[str] = None
) -> Dict[str, Any]:
    """Build intelligent CV-based questions from candidate's actual resume data."""
    prev_set = set((q or "").strip().lower() for q in (previous_questions or []))
    rng = random.Random(f"{role}_{question_num}_{random.randint(1, 999999)}")

    # Technical questions about their actual skills
    tech_questions = []
    for skill in (skills or [])[:5]:
        if len(skill) > 2:
            tech_questions.append({
                "question_text": f"You listed {skill} as a skill on your resume. Can you explain how you used {skill} in a real project, and describe a challenging problem you solved with it?",
                "topic": skill,
                "difficulty": difficulty,
                "expected_concepts": [f"{skill} usage", "Problem-solving", "Practical application", "Challenges faced"],
                "cv_reference": f"Skill: {skill}"
            })

    # Project-based questions
    project_questions = []
    for proj in (projects or [])[:3]:
        title = proj.get("title", "")
        if title:
            project_questions.append({
                "question_text": f"Tell me about your project '{title}'. What was the architecture you used, what technical challenges did you face, and how did you overcome them?",
                "topic": "Project Architecture",
                "difficulty": difficulty,
                "expected_concepts": ["System design", "Problem-solving", "Technical decisions", "Lessons learned"],
                "cv_reference": f"Project: {title}"
            })

    # HR/behavioral questions referencing their experience
    hr_questions = [
        {
            "question_text": "Based on your resume, you've worked on several projects. Can you describe a situation where you had to collaborate with a team to meet a tight deadline?",
            "topic": "Teamwork & Collaboration",
            "difficulty": difficulty,
            "expected_concepts": ["Team collaboration", "Time management", "Communication", "Delivery under pressure"],
            "cv_reference": "General experience"
        },
        {
            "question_text": "What motivated you to pursue the skills and technologies listed on your resume, and how do you stay updated with the latest developments in your field?",
            "topic": "Learning & Growth",
            "difficulty": difficulty,
            "expected_concepts": ["Continuous learning", "Self-motivation", "Technical curiosity", "Growth mindset"],
            "cv_reference": "Skills section"
        },
    ]

    all_questions = []
    if interview_type == "Technical":
        all_questions = tech_questions + project_questions
    elif interview_type == "HR":
        all_questions = hr_questions + project_questions
    else:  # Mixed
        all_questions = tech_questions + project_questions + hr_questions

    if not all_questions:
        all_questions = hr_questions

    # Filter previously asked
    unasked = [q for q in all_questions if q["question_text"].strip().lower() not in prev_set]
    if not unasked:
        unasked = all_questions

    return rng.choice(unasked)


def get_fallback_recommendations(overall_score: float, skills: List[str], role: str, company: str) -> Dict[str, Any]:
    """Fallback recommendations when Gemini API is unavailable."""
    readiness = "Ready" if overall_score >= 8.0 else ("Almost Ready" if overall_score >= 6.0 else "Needs Preparation")
    skill_list = skills[:5] if skills else ["Programming fundamentals"]

    return {
        "overall_readiness": readiness,
        "readiness_score": round(overall_score, 1),
        "cv_gaps": [f"Advanced {role} domain knowledge", "System design patterns", "Production deployment experience"],
        "cv_strengths": skill_list[:3],
        "interview_skill_gaps": ["Deep technical explanations", "Concrete example-based answers"] if overall_score < 7 else ["Edge case handling"],
        "top_recommendations": [
            {"priority": "High", "action": f"Practice {role} interview questions daily", "reason": "Consistent practice builds confidence and recall speed"},
            {"priority": "Medium", "action": "Build 1-2 portfolio projects showcasing your skills", "reason": "Demonstrable projects strengthen your candidacy significantly"},
            {"priority": "Low", "action": "Join developer communities on LinkedIn and GitHub", "reason": "Networking opens referral opportunities at companies like " + company}
        ],
        "learning_path": [
            {"topic": f"{role} Core Concepts", "resource": "Official Documentation", "url": "https://docs.python.org/3/" if "Python" in role else "https://developer.mozilla.org", "estimated_time": "2 weeks"},
            {"topic": "System Design", "resource": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer", "estimated_time": "3 weeks"},
            {"topic": "Data Structures & Algorithms", "resource": "LeetCode", "url": "https://leetcode.com", "estimated_time": "4 weeks"}
        ],
        "cv_improvement_tips": [
            f"Add measurable impact metrics to each project (e.g., 'reduced loading time by 40%')",
            f"Tailor your summary section specifically for {role} positions at {company}",
            "Add a GitHub profile link with active repositories"
        ],
        "next_steps": f"You scored {overall_score}/10 in your interview. {'Great performance! Focus on refining edge cases.' if overall_score >= 7 else 'Keep practicing! Consistency is key.'} Review the learning path below and set a 30-day preparation plan."
    }


# ==========================================
# DYNAMIC ROLE-BASED QUESTION POOL & GENERATOR
# ==========================================

ROLE_QUESTIONS_BANK = {
    "Python Developer": [
        {
            "question_text": "How do Python's memory management and garbage collection (reference counting & cyclic GC) work, and how does the GIL impact multithreading vs multiprocessing?",
            "topic": "Python Core & GIL",
            "expected_concepts": ["Reference Counting", "Generational GC", "GIL", "Multiprocessing vs Asyncio"]
        },
        {
            "question_text": "Explain Python decorators, generators, and context managers (__enter__ / __exit__). How do generators optimize memory efficiency when parsing large log files?",
            "topic": "Python Advanced Syntax",
            "expected_concepts": ["Decorators", "Generators / yield", "Context Managers", "Memory Efficiency"]
        },
        {
            "question_text": "Describe the request lifecycle in FastAPI or Django. How do you optimize ORM database queries to prevent the N+1 query problem?",
            "topic": "Python Web & ORM",
            "expected_concepts": ["Request Lifecycle", "ORM Query Optimization", "select_related / prefetch_related", "N+1 Query Problem"]
        },
        {
            "question_text": "Compare time and space complexity of Python lists, dicts, and sets under the hood. How does Python resolve dictionary hash collisions?",
            "topic": "Data Structures in Python",
            "expected_concepts": ["Hash Table", "Open Addressing", "O(1) Lookup", "List Resizing"]
        },
        {
            "question_text": "How do you handle asynchronous background task queues and concurrency in Python using Celery, Redis, or Asyncio?",
            "topic": "System Concurrency",
            "expected_concepts": ["Asyncio", "Celery Workers", "Task Queues", "Redis Broker"]
        },
        {
            "question_text": "Explain Python type hints (typing module), Pydantic data validation schemas, and how static analysis tools like mypy improve backend reliability.",
            "topic": "Type Safety & Pydantic",
            "expected_concepts": ["Type Hints", "Pydantic Schemas", "Mypy Static Analysis", "Data Validation"]
        },
        {
            "question_text": "How do Metaclasses work in Python? Explain __new__ vs __init__, class decorators, and dynamic attribute resolution using __getattr__.",
            "topic": "Metaprogramming",
            "expected_concepts": ["Metaclasses", "__new__ vs __init__", "__getattr__ vs __getattribute__", "Class Decorators"]
        },
        {
            "question_text": "Explain deep copy vs shallow copy in Python. What are the pitfalls of using mutable default arguments in Python function definitions?",
            "topic": "Python Fundamentals",
            "expected_concepts": ["Shallow vs Deep Copy", "Mutable Defaults", "copy.deepcopy()", "Object Identity vs Equality"]
        },
        {
            "question_text": "How do you structure database connection pooling in SQLAlchemy/Asyncpg to handle high-concurrency requests safely?",
            "topic": "Database & Connection Pooling",
            "expected_concepts": ["Connection Pooling", "SQLAlchemy Engine", "Asyncpg", "Transaction Isolation"]
        },
        {
            "question_text": "Describe unit testing patterns in Python using pytest, fixtures, parameterization, and mocking external HTTP endpoints with unittest.mock.",
            "topic": "Testing & Mocking",
            "expected_concepts": ["pytest Fixtures", "Parameterization", "unittest.mock", "Patching"]
        }
    ],
    "Java Developer": [
        {
            "question_text": "Explain the JVM Architecture (Heap, Stack, Metaspace) and how Java Garbage Collectors like G1GC or ZGC manage object lifecycles.",
            "topic": "JVM & Memory Management",
            "expected_concepts": ["Heap vs Stack", "Metaspace", "G1GC / ZGC", "Mark and Sweep"]
        },
        {
            "question_text": "What is the difference between an Abstract Class and an Interface in Java? When would you use Java 8+ default and static interface methods?",
            "topic": "Java OOP Principles",
            "expected_concepts": ["Abstraction", "Multiple Inheritance", "Default Methods", "Polymorphism"]
        },
        {
            "question_text": "Describe Java Concurrency mechanisms: synchronized blocks, ReentrantLock, volatile keyword, and ExecutorService thread pools.",
            "topic": "Java Concurrency",
            "expected_concepts": ["Thread Safety", "Volatile Memory", "ReentrantLock", "ExecutorService"]
        },
        {
            "question_text": "How does Spring Boot Dependency Injection (IoC) work? Explain Spring Bean scopes and @Transactional propagation levels.",
            "topic": "Spring Framework",
            "expected_concepts": ["Inversion of Control", "Bean Scopes", "Dependency Injection", "@Transactional"]
        },
        {
            "question_text": "How does HashMap work internally in Java 8+? Explain how bucket arrays convert to red-black trees under heavy hash collisions.",
            "topic": "Java Collections",
            "expected_concepts": ["Hash Code & Equals", "Bucket Array", "Red-Black Tree", "Load Factor"]
        },
        {
            "question_text": "Explain the Java 8 Stream API: intermediate vs terminal operations, parallel streams, and memory overhead during grouping operations.",
            "topic": "Java Streams & Functional API",
            "expected_concepts": ["Stream API", "Intermediate vs Terminal", "Collectors.groupingBy()", "Parallel Streams"]
        },
        {
            "question_text": "Compare checked vs unchecked exceptions in Java. How does try-with-resources guarantee resource cleanup for AutoCloseable interfaces?",
            "topic": "Exception Handling",
            "expected_concepts": ["Checked vs Unchecked Exceptions", "try-with-resources", "AutoCloseable", "Custom Exceptions"]
        },
        {
            "question_text": "Describe Spring Security architecture: SecurityFilterChain, JWT authentication tokens, and Role-Based Access Control (RBAC).",
            "topic": "Spring Security",
            "expected_concepts": ["SecurityFilterChain", "JWT Authentication", "RBAC", "UserDetailsService"]
        },
        {
            "question_text": "Explain JPA / Hibernate entity states (Transient, Persistent, Detached) and how L1/L2 caches reduce database queries.",
            "topic": "Hibernate ORM",
            "expected_concepts": ["Entity States", "L1 / L2 Cache", "Lazy vs Eager Loading", "N+1 Problem"]
        },
        {
            "question_text": "How do you design Java Microservices using Spring Cloud, Eureka Service Discovery, and Resilience4j Circuit Breakers?",
            "topic": "Microservices in Java",
            "expected_concepts": ["Eureka Discovery", "Circuit Breaker", "Resilience4j", "API Gateway"]
        }
    ],
    "Data Analyst": [
        {
            "question_text": "Explain SQL window functions like ROW_NUMBER(), RANK(), DENSE_RANK(), and NTILE(). Write a conceptual query to find the top 3 sales per region.",
            "topic": "SQL Analytics & Window Functions",
            "expected_concepts": ["Window Functions", "OVER(PARTITION BY)", "RANK vs DENSE_RANK", "CTEs"]
        },
        {
            "question_text": "How do you handle missing values, outliers (Z-score/IQR), and data normalization in Python Pandas before performing statistical reporting?",
            "topic": "Data Cleaning & Wrangling",
            "expected_concepts": ["Pandas fillna/dropna", "IQR Outlier Detection", "Standardization vs Normalization", "Imputation"]
        },
        {
            "question_text": "Define key business KPIs like Customer Acquisition Cost (CAC), Lifetime Value (LTV), and Churn Rate. How would you design an executive dashboard to track them?",
            "topic": "Business Intelligence & KPIs",
            "expected_concepts": ["CAC & LTV", "Churn Rate", "Cohort Analysis", "Dashboard Visualization"]
        },
        {
            "question_text": "Explain the statistical principles of A/B Testing: hypothesis formulation, null hypothesis, p-values, and statistical significance testing.",
            "topic": "Statistics & A/B Testing",
            "expected_concepts": ["Null Hypothesis", "p-value", "Alpha Level", "Statistical Power"]
        },
        {
            "question_text": "Compare SQL Joins (INNER, LEFT, RIGHT, FULL OUTER) and explain how B-Tree indexing speeds up query aggregation on multi-million row tables.",
            "topic": "SQL Query Optimization",
            "expected_concepts": ["JOIN Types", "B-Tree Indexing", "GROUP BY Aggregations", "Query Execution Plan"]
        },
        {
            "question_text": "Explain data visualization principles: when should you use a line chart versus a stacked bar chart versus a scatter plot?",
            "topic": "Data Visualization",
            "expected_concepts": ["Chart Selection", "Data Density", "Trend Analysis", "Avoiding Misleading Visuals"]
        },
        {
            "question_text": "How do you perform user retention cohort analysis and conversion funnel analysis using SQL and Pandas?",
            "topic": "Cohort Analysis",
            "expected_concepts": ["Cohort Analysis", "User Retention", "Funnel Conversion", "Date Truncation"]
        },
        {
            "question_text": "Compare Relational Star Schema vs Snowflake Schema in Data Warehousing. What are Fact tables and Dimension tables?",
            "topic": "Data Warehousing",
            "expected_concepts": ["Star Schema", "Snowflake Schema", "Fact Tables", "Dimension Tables"]
        },
        {
            "question_text": "How do you automate routine data extraction and reporting pipelines using Python scripts and automated scheduling?",
            "topic": "Data Automation",
            "expected_concepts": ["Pandas Scripting", "ETL Pipelines", "Automated Reporting", "Schedule Trigger"]
        },
        {
            "question_text": "What steps do you take during Exploratory Data Analysis (EDA) to detect skewness, multi-collinearity, and data distribution anomalies?",
            "topic": "Exploratory Data Analysis",
            "expected_concepts": ["EDA", "Skewness & Kurtosis", "Multi-collinearity", "Correlation Matrix"]
        }
    ],
    "Data Scientist": [
        {
            "question_text": "Explain Precision, Recall, F1-Score, and ROC-AUC. Which metric would you optimize when building a model for detecting rare medical anomalies on imbalanced data?",
            "topic": "ML Model Evaluation",
            "expected_concepts": ["Precision vs Recall", "F1-Score", "ROC-AUC", "Imbalanced Data / SMOTE"]
        },
        {
            "question_text": "Describe the Bias-Variance tradeoff. How do L1 (Lasso) and L2 (Ridge) regularization penalties help prevent machine learning overfitting?",
            "topic": "Machine Learning Algorithms",
            "expected_concepts": ["Overfitting vs Underfitting", "L1 Lasso (Sparsity)", "L2 Ridge (Weight Penalty)", "Cross-Validation"]
        },
        {
            "question_text": "Compare Gradient Boosted Decision Trees (XGBoost/LightGBM) with Deep Neural Networks. In what practical scenarios does GBDT outperform Neural Networks?",
            "topic": "Tree-based Models vs Deep Learning",
            "expected_concepts": ["XGBoost / LightGBM", "Tabular Data Efficiency", "Gradient Boosting", "Feature Importance"]
        },
        {
            "question_text": "Explain how Transformers and Self-Attention mechanisms work compared to traditional recurrent networks (RNNs/LSTMs) in Natural Language Processing.",
            "topic": "Deep Learning & NLP",
            "expected_concepts": ["Self-Attention", "Query Key Value Vectors", "Transformer Architecture", "Vanishing Gradient"]
        },
        {
            "question_text": "How do you deploy ML models into production REST endpoints, monitor data/concept drift, and implement continuous model retraining pipelines?",
            "topic": "MLOps & Model Deployment",
            "expected_concepts": ["MLOps", "Model Serving REST API", "Data Drift Detection", "Feature Store"]
        },
        {
            "question_text": "Explain Dimensionality Reduction using PCA (Principal Component Analysis) vs t-SNE / UMAP. How do you interpret explained variance ratio?",
            "topic": "Dimensionality Reduction",
            "expected_concepts": ["PCA", "Eigenvalues / Eigenvectors", "t-SNE / UMAP", "Explained Variance"]
        },
        {
            "question_text": "Compare K-Means vs DBSCAN vs Hierarchical Clustering. How do you determine the optimal number of clusters using the Silhouette score or Elbow method?",
            "topic": "Unsupervised Clustering",
            "expected_concepts": ["K-Means", "DBSCAN", "Silhouette Score", "Elbow Method"]
        },
        {
            "question_text": "How do you resolve vanishing and exploding gradients in deep neural networks? Compare Adam, RMSprop, and SGD optimizers.",
            "topic": "Neural Network Optimization",
            "expected_concepts": ["Vanishing Gradient", "Adam Optimizer", "Batch Normalization", "Dropout"]
        },
        {
            "question_text": "What feature engineering techniques do you use for high-cardinality categorical variables (One-hot vs Target Encoding)?",
            "topic": "Feature Engineering",
            "expected_concepts": ["Target Encoding", "One-Hot Encoding", "High-Cardinality", "Data Leakage"]
        },
        {
            "question_text": "Compare Fine-Tuning Large Language Models vs Retrieval-Augmented Generation (RAG) using vector databases (FAISS / Chroma DB).",
            "topic": "Generative AI & RAG",
            "expected_concepts": ["RAG Architecture", "Vector Embeddings", "FAISS / Chroma", "LLM Fine-Tuning"]
        }
    ],
    "Full Stack Developer": [
        {
            "question_text": "Explain RESTful API design principles, standard HTTP status codes (200, 201, 400, 401, 403, 500), and CORS preflight options request handling.",
            "topic": "Web API Architecture",
            "expected_concepts": ["RESTful Standards", "HTTP Status Codes", "CORS Preflight", "JSON Payloads"]
        },
        {
            "question_text": "How do you manage client-side state in modern frontend frameworks (React State/Context API/Redux) versus stateless backend session authentication?",
            "topic": "State & Authentication",
            "expected_concepts": ["State vs Props", "Context API / Redux", "Stateless Backend JWT", "Re-rendering"]
        },
        {
            "question_text": "Compare Relational Databases (PostgreSQL/MySQL) with NoSQL Document Stores (MongoDB). When would you choose relational schemas over NoSQL?",
            "topic": "Database Architecture",
            "expected_concepts": ["ACID vs BASE", "Schema Flexibility", "Relational Joins", "Scalability Trade-offs"]
        },
        {
            "question_text": "What are OWASP Top 10 security vulnerabilities like SQL Injection, Cross-Site Scripting (XSS), and CSRF? How do you defend full-stack applications against them?",
            "topic": "Full Stack Security",
            "expected_concepts": ["SQL Injection Prevention", "XSS Sanitization", "CSRF Tokens", "JWT / HTTPS"]
        },
        {
            "question_text": "How do you architect asynchronous microservices communication using REST, gRPC, or message brokers like Kafka / RabbitMQ?",
            "topic": "System Architecture",
            "expected_concepts": ["Microservices", "Event-Driven Architecture", "Kafka / RabbitMQ", "Service Mesh"]
        },
        {
            "question_text": "Compare Server-Side Rendering (SSR in Next.js) with Client-Side Rendering (CSR in React SPA). What are the SEO and performance implications?",
            "topic": "SSR vs CSR Architecture",
            "expected_concepts": ["SSR vs CSR", "Next.js", "SEO Optimization", "First Contentful Paint"]
        },
        {
            "question_text": "How do you design database indexing strategies (B-Tree, Hash) and Redis caching layers (Cache-Aside pattern) for full-stack apps?",
            "topic": "Caching & Indexing",
            "expected_concepts": ["Redis Cache-Aside", "B-Tree Indexing", "Query Optimization", "Cache Invalidation"]
        },
        {
            "question_text": "Compare WebSockets, Server-Sent Events (SSE), and HTTP Long Polling for building real-time interactive full-stack features.",
            "topic": "Real-time Web Communication",
            "expected_concepts": ["WebSockets", "Server-Sent Events", "Long Polling", "Bi-directional Flow"]
        },
        {
            "question_text": "How do you handle distributed transactions across microservices using the Saga Pattern or Two-Phase Commit (2PC)?",
            "topic": "Distributed Systems",
            "expected_concepts": ["Saga Pattern", "Choreography vs Orchestration", "2PC", "Eventual Consistency"]
        },
        {
            "question_text": "How do you structure Docker Compose files and GitHub Actions CI/CD workflows for multi-container full-stack deployments?",
            "topic": "Full Stack DevOps & CI/CD",
            "expected_concepts": ["Docker Compose", "GitHub Actions", "Multi-stage Build", "Environment Secrets"]
        }
    ],
    "Frontend Developer": [
        {
            "question_text": "Explain the JavaScript Event Loop, Call Stack, Web APIs, Microtask Queue (Promises), and Macrotask Queue (setTimeout).",
            "topic": "JavaScript Event Loop",
            "expected_concepts": ["Event Loop", "Call Stack", "Microtask Queue", "Asynchronous Execution"]
        },
        {
            "question_text": "Compare CSS Flexbox vs CSS Grid layout systems. How do media queries and responsive units (rem, em, vh, vw) enable fluid UI rendering across devices?",
            "topic": "CSS & Responsive Design",
            "expected_concepts": ["Flexbox vs Grid", "Responsive Design", "Media Queries", "Relative Units"]
        },
        {
            "question_text": "How do React Hooks like useState, useEffect, useMemo, and useCallback work to optimize Virtual DOM reconciliation and prevent unnecessary re-renders?",
            "topic": "React Performance",
            "expected_concepts": ["Virtual DOM", "useMemo / useCallback", "Dependency Arrays", "Render Cycles"]
        },
        {
            "question_text": "What are Core Web Vitals (LCP, FID/INP, CLS)? How do you optimize web application bundle size, lazy loading, and critical rendering path?",
            "topic": "Web Performance Optimization",
            "expected_concepts": ["LCP & CLS", "Code Splitting / Lazy Loading", "Tree Shaking", "Critical Path"]
        },
        {
            "question_text": "Explain DOM event propagation (capturing phase vs bubbling phase) and how event delegation improves performance on dynamic data lists.",
            "topic": "DOM Architecture",
            "expected_concepts": ["Event Bubbling", "Event Capturing", "Event Delegation", "target vs currentTarget"]
        },
        {
            "question_text": "How do Content Security Policies (CSP) and HttpOnly cookie flags protect frontend web apps against DOM-based Cross-Site Scripting (XSS)?",
            "topic": "Frontend Security",
            "expected_concepts": ["Content Security Policy", "XSS Prevention", "HttpOnly Cookies", "DOM Sanitization"]
        },
        {
            "question_text": "Explain TypeScript advanced features in React: Interfaces vs Types, Generics, Union Types, and Strict Null Checking.",
            "topic": "TypeScript in React",
            "expected_concepts": ["TypeScript Interfaces", "Generics", "Type Narrowing", "Strict Null Checks"]
        },
        {
            "question_text": "Compare Redux Toolkit, React Context API, and Zustand for state management in large scale React frontend applications.",
            "topic": "Frontend State Management",
            "expected_concepts": ["Redux Toolkit", "Context API", "Zustand", "Immutable Updates"]
        },
        {
            "question_text": "How does Client-Side Routing work in Single Page Applications (React Router)? How do you implement code-split route boundaries?",
            "topic": "SPA Routing & Code-Splitting",
            "expected_concepts": ["React Router", "Dynamic Import", "React.lazy & Suspense", "Route Splitting"]
        },
        {
            "question_text": "How do you implement Web Accessibility (a11y) standards: semantic HTML5 tags, ARIA roles/attributes, and keyboard focus management?",
            "topic": "Web Accessibility (a11y)",
            "expected_concepts": ["ARIA Roles", "Semantic HTML5", "Keyboard Focus", "Screen Readers"]
        }
    ],
    "DevOps / Cloud Engineer": [
        {
            "question_text": "How do Docker containerization, multi-stage builds, and layer caching work? How do you minimize container image size and harden container security?",
            "topic": "Containerization",
            "expected_concepts": ["Multi-stage Builds", "Layer Caching", "Non-root Users", "Base Image Selection"]
        },
        {
            "question_text": "Explain Kubernetes Core Objects: Pods, Deployments, Services (ClusterIP/NodePort/LoadBalancer), and Ingress Controllers.",
            "topic": "Kubernetes Orchestration",
            "expected_concepts": ["Pods & Deployments", "ClusterIP / Ingress", "ConfigMaps & Secrets", "Horizontal Pod Autoscaler"]
        },
        {
            "question_text": "How do you design an automated CI/CD pipeline using GitHub Actions or Jenkins with automated unit testing and canary/blue-green deployments?",
            "topic": "CI/CD Automation",
            "expected_concepts": ["CI/CD Pipeline", "Automated Testing", "Blue-Green / Canary Deployments", "Artifact Management"]
        },
        {
            "question_text": "What is Infrastructure as Code (IaC) using Terraform? Explain Terraform state management, modules, and drift detection.",
            "topic": "Infrastructure as Code",
            "expected_concepts": ["Terraform State", "Modules & Providers", "Terraform Plan / Apply", "Drift Remediation"]
        },
        {
            "question_text": "Describe cloud observability using Prometheus metrics collection, Grafana dashboards, ELK/EFK centralized logging, and SLA/SLO uptime tracking.",
            "topic": "Cloud Observability",
            "expected_concepts": ["Prometheus Metrics", "Grafana Dashboards", "Centralized Logging", "SLO / SLA Monitoring"]
        },
        {
            "question_text": "Explain the Principle of Least Privilege in Cloud IAM. How do AWS IAM Roles, IAM Policies, and KMS Keys secure cloud infrastructure?",
            "topic": "Cloud IAM & Security",
            "expected_concepts": ["Least Privilege", "IAM Roles & Policies", "KMS Encryption", "Security Groups"]
        },
        {
            "question_text": "What is a Service Mesh (Istio / Linkerd)? How does it handle mTLS encryption, traffic splitting, and telemetry across Kubernetes pods?",
            "topic": "Service Mesh & Networking",
            "expected_concepts": ["Service Mesh", "Istio / Linkerd", "mTLS Encryption", "Traffic Splitting"]
        },
        {
            "question_text": "Compare AWS S3 Bucket Security Policies, RDS Multi-AZ Failover, and Disaster Recovery backup strategies (RTO / RPO).",
            "topic": "Cloud Storage & DR",
            "expected_concepts": ["Multi-AZ Failover", "RTO & RPO", "S3 Bucket Policies", "Disaster Recovery"]
        },
        {
            "question_text": "How do you manage secret rotation safely using HashiCorp Vault or AWS Secrets Manager inside CI/CD pipelines?",
            "topic": "Secrets Management",
            "expected_concepts": ["HashiCorp Vault", "Secrets Manager", "Secret Rotation", "Environment Injection"]
        },
        {
            "question_text": "Describe Cloud FinOps cost management: spot instances vs reserved instances, auto-scaling policies, and resource tagging.",
            "topic": "Cloud FinOps & Cost Tuning",
            "expected_concepts": ["Spot vs Reserved Instances", "FinOps", "Auto-scaling Triggers", "Resource Tagging"]
        }
    ],
    "QA / Automation Engineer": [
        {
            "question_text": "Explain Page Object Model (POM) design pattern in Selenium / Playwright / PyTest. How does it improve test suite maintainability?",
            "topic": "Test Automation Architecture",
            "expected_concepts": ["Page Object Model", "Locators / Selectors", "Code Reusability", "Maintainability"]
        },
        {
            "question_text": "Describe the Test Pyramid (Unit, Integration, E2E Tests). How do you automate REST API testing using Postman or REST Assured?",
            "topic": "API Testing & Strategy",
            "expected_concepts": ["Test Pyramid", "API Automation", "HTTP Assertions", "Mocking Dependencies"]
        },
        {
            "question_text": "How do you identify edge cases, apply Equivalence Partitioning, and perform Boundary Value Analysis when creating test specifications?",
            "topic": "Test Case Design",
            "expected_concepts": ["Boundary Value Analysis", "Equivalence Partitioning", "Edge Case Discovery", "Defect Lifecycle"]
        },
        {
            "question_text": "How do you integrate automated test suites into CI/CD build triggers to perform regression testing on pull requests?",
            "topic": "CI/CD Test Integration",
            "expected_concepts": ["Regression Test Suite", "PR Quality Gates", "Headless Execution", "Test Reporting"]
        },
        {
            "question_text": "Compare Load Testing vs Stress Testing. How would you use JMeter or Locust to simulate concurrent traffic and measure response latency?",
            "topic": "Performance & Load Testing",
            "expected_concepts": ["Load vs Stress Testing", "JMeter / Locust", "Ramp-up Users", "Throughput & Latency"]
        },
        {
            "question_text": "How do you generate dynamic test data (Faker) and ensure clean test database teardown between automated test runs?",
            "topic": "Test Data Management",
            "expected_concepts": ["Test Data Generation", "Faker Library", "Database Teardown", "Test Isolation"]
        },
        {
            "question_text": "Explain Appium mobile automation framework: locator strategies for iOS vs Android, native vs hybrid application testing.",
            "topic": "Mobile Test Automation",
            "expected_concepts": ["Appium Framework", "iOS vs Android Locators", "Native vs Hybrid", "Mobile Drivers"]
        },
        {
            "question_text": "How do you perform cloud-based cross-browser and cross-device testing using BrowserStack or SauceLabs?",
            "topic": "Cross-Browser Testing",
            "expected_concepts": ["BrowserStack", "SauceLabs", "Cross-Browser Matrix", "Responsive Verification"]
        },
        {
            "question_text": "What is Contract Testing using Pact? How does it validate API request/response schemas between microservices teams?",
            "topic": "Contract Testing",
            "expected_concepts": ["Pact Framework", "Contract Testing", "Consumer vs Producer", "Schema Validation"]
        },
        {
            "question_text": "How do you diagnose and eliminate flaky automated tests? Compare explicit waits vs implicit waits vs fluent waits.",
            "topic": "Flaky Test Remediation",
            "expected_concepts": ["Explicit vs Implicit Waits", "Flaky Test Remediation", "Synchronization Barriers", "Retry Policies"]
        }
    ],
    "HR / Behavioral": [
        {
            "question_text": "Describe a scenario where you faced significant conflict or disagreement with a team member or stakeholder. How did you resolve it constructively?",
            "topic": "Conflict Resolution",
            "expected_concepts": ["Constructive Dialogue", "Empathy & Active Listening", "Professional Resolution", "Team Harmony"]
        },
        {
            "question_text": "Tell me about a project that failed or missed a critical production deadline. What root causes were identified, and what did you learn?",
            "topic": "Accountability & Post-Mortem",
            "expected_concepts": ["Ownership & Accountability", "Post-mortem Analysis", "Continuous Improvement", "Risk Mitigation"]
        },
        {
            "question_text": "How do you prioritize your daily deliverables when faced with multiple competing urgent requests from different engineering stakeholders?",
            "topic": "Time Management & Prioritization",
            "expected_concepts": ["Eisenhower Matrix", "Stakeholder Communication", "Task Prioritization", "Setting Expectations"]
        },
        {
            "question_text": "Describe a scenario where you had to adapt quickly to sudden requirement changes or unfamiliar technology stacks. How did you handle it?",
            "topic": "Adaptability & Resilience",
            "expected_concepts": ["Adaptability", "Self-Directed Learning", "Resilience", "Agile Mindset"]
        },
        {
            "question_text": "What are your core career goals for the next 3 to 5 years, and how does working at this company align with your professional growth?",
            "topic": "Career Goals & Alignment",
            "expected_concepts": ["Career Ambition", "Company Alignment", "Continuous Learning", "Long-term Commitment"]
        },
        {
            "question_text": "Describe your experience mentoring junior engineers or onboarding new team members. How do you foster inclusive team growth?",
            "topic": "Leadership & Mentorship",
            "expected_concepts": ["Mentorship", "Peer Code Reviews", "Knowledge Sharing", "Inclusive Culture"]
        },
        {
            "question_text": "How do you handle receiving tough constructive feedback during performance reviews? Can you give an example of an area you improved?",
            "topic": "Receiving Feedback",
            "expected_concepts": ["Growth Mindset", "Receiving Feedback", "Self-Reflection", "Actionable Improvement"]
        },
        {
            "question_text": "How do you explain complex technical architecture, system trade-offs, or delays to non-technical business executive stakeholders?",
            "topic": "Stakeholder Communication",
            "expected_concepts": ["Non-Technical Communication", "Simplifying Complexity", "Managing Expectations", "Business Value"]
        },
        {
            "question_text": "How do you maintain high work quality and prevent personal burnout during intense release crunches or high-pressure deadlines?",
            "topic": "Work-Life Balance",
            "expected_concepts": ["Burnout Prevention", "Work-Life Balance", "Stress Management", "Quality Standards"]
        },
        {
            "question_text": "What steps do you take to ensure respectful, diverse, and inclusive collaboration within cross-functional engineering teams?",
            "topic": "Diversity & Inclusion",
            "expected_concepts": ["Diversity & Inclusion", "Psychological Safety", "Respectful Communication", "Team Collaboration"]
        }
    ]
}

def get_fallback_question(
    company: str,
    role: str,
    difficulty: str,
    interview_type: str,
    question_num: int,
    skills: List[str] = None,
    previous_questions: List[str] = None
) -> Dict[str, Any]:
    """Provide realistic, dynamically randomized, non-repeating role-matched interview questions."""
    role_lower = (role or "").strip().lower()
    matched_bank = None
    
    # 1. Direct role match or fuzzy match
    if role in ROLE_QUESTIONS_BANK:
        matched_bank = ROLE_QUESTIONS_BANK[role]
    else:
        if "java" in role_lower and "javascript" not in role_lower:
            matched_bank = ROLE_QUESTIONS_BANK["Java Developer"]
        elif "analyst" in role_lower or "analytics" in role_lower:
            matched_bank = ROLE_QUESTIONS_BANK["Data Analyst"]
        elif "data" in role_lower or "machine" in role_lower or "science" in role_lower or "ai" in role_lower:
            matched_bank = ROLE_QUESTIONS_BANK["Data Scientist"]
        elif "front" in role_lower or "react" in role_lower or "ui" in role_lower or "web" in role_lower:
            matched_bank = ROLE_QUESTIONS_BANK["Frontend Developer"]
        elif "devops" in role_lower or "cloud" in role_lower or "sre" in role_lower or "docker" in role_lower:
            matched_bank = ROLE_QUESTIONS_BANK["DevOps / Cloud Engineer"]
        elif "full" in role_lower or "stack" in role_lower:
            matched_bank = ROLE_QUESTIONS_BANK["Full Stack Developer"]
        elif "qa" in role_lower or "test" in role_lower or "automation" in role_lower:
            matched_bank = ROLE_QUESTIONS_BANK["QA / Automation Engineer"]
        elif "hr" in role_lower or "behavior" in role_lower or "manager" in role_lower:
            matched_bank = ROLE_QUESTIONS_BANK["HR / Behavioral"]
        else:
            matched_bank = ROLE_QUESTIONS_BANK["Python Developer"]

    # 2. Filter out questions already asked in this session
    prev_set = set((q or "").strip().lower() for q in (previous_questions or []))
    unasked = [q for q in matched_bank if q["question_text"].strip().lower() not in prev_set]
    
    if not unasked:
        unasked = matched_bank

    # 3. Dynamic non-repeating randomization seed using high-entropy session values
    seed_key = f"{company}_{role}_{question_num}_{len(previous_questions or [])}_{random.randint(1, 1000000)}"
    rng = random.Random(seed_key)
    selected_q = rng.choice(unasked).copy()
    
    # 4. Optional Resume Skill Integration
    if skills:
        skill_sample = [s for s in skills if isinstance(s, str) and len(s) > 2]
        if skill_sample:
            selected_skill = rng.choice(skill_sample)
            if selected_skill not in selected_q["expected_concepts"]:
                selected_q["expected_concepts"].append(selected_skill)

    selected_q["difficulty"] = difficulty
    return selected_q

def get_fallback_evaluation(question_text: str, user_answer: str, expected_concepts: List[str]) -> Dict[str, Any]:
    """Provide accurate dynamic heuristic scoring when Gemini API is offline."""
    if is_non_answer(user_answer):
        exp_list = expected_concepts if expected_concepts else ["Core domain concepts"]
        return {
            "correctness_score": 0.0,
            "completeness_score": 0.0,
            "technical_accuracy_score": 0.0,
            "communication_score": 0.0,
            "confidence_score": 0.0,
            "total_score": 0.0,
            "best_answer": f"Model answer for '{question_text[:70]}...' should cover: {', '.join(exp_list)}.",
            "missing_concepts": exp_list,
            "feedback": "Your input is not a technical response to this question (e.g. greeting, test word, or admission of no answer). 0.0 marks awarded."
        }

    answer_words = user_answer.strip().lower().split()
    word_count = len(answer_words)

    # Check keyword matches with expected_concepts
    matched_concepts = []
    if expected_concepts:
        for concept in expected_concepts:
            concept_words = concept.lower().split()
            if any(w in user_answer.lower() for w in concept_words if len(w) > 2):
                matched_concepts.append(concept)
    
    match_ratio = len(matched_concepts) / max(1, len(expected_concepts)) if expected_concepts else 0.0

    # Strict evaluation for short or non-technical answers
    if word_count < 5 and match_ratio == 0:
        base_score = 0.0
        feedback = "Answer is extremely brief and contains no relevant technical content or expected concepts. 0.0 marks awarded."
    elif word_count < 15 and match_ratio == 0:
        base_score = 1.0
        feedback = "Response is missing all expected technical concepts and keywords for this topic. Please provide detailed explanations."
    elif word_count < 25 and match_ratio < 0.4:
        base_score = 4.0
        feedback = "Partial answer with limited technical depth. Try explaining underlying principles, code syntax, and edge cases."
    elif match_ratio >= 0.7:
        base_score = 8.5
        feedback = "Excellent response covering major expected technical concepts and principles."
    elif match_ratio >= 0.3:
        base_score = 6.5
        feedback = "Satisfactory answer covering foundational aspects, but could include deeper architectural details."
    else:
        base_score = 5.0
        feedback = "Fair answer, but lacks specific terminology and expected technical keywords."

    missing = [c for c in (expected_concepts or []) if c not in matched_concepts]
    if not missing:
        missing = ["Edge case handling", "Performance optimizations"]

    return {
        "correctness_score": min(10.0, round(base_score, 1)),
        "completeness_score": min(10.0, round(base_score * 0.9, 1)),
        "technical_accuracy_score": min(10.0, round(base_score, 1)),
        "communication_score": min(10.0, round(base_score * 1.05, 1)),
        "confidence_score": min(10.0, round(base_score, 1)),
        "total_score": round(base_score, 1),
        "best_answer": f"An ideal answer to '{question_text[:60]}...' thoroughly explains the underlying concepts, key syntax, performance trade-offs, and practical implementations.",
        "missing_concepts": missing[:3],
        "feedback": feedback
    }

def get_fallback_report(overall_score: float, qa_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Provide structured report metadata fallback when Gemini API is offline."""
    return {
        "python_score": round(min(10.0, overall_score + 0.5), 1),
        "sql_score": round(max(0.0, overall_score - 0.5), 1),
        "dbms_score": round(overall_score, 1),
        "oop_score": round(min(10.0, overall_score + 0.2), 1),
        "communication_score": round(min(10.0, overall_score + 0.8), 1),
        "strengths": [
            "Strong grasp of core concepts and domain fundamentals",
            "Clear technical communication and structured problem solving",
            "Good understanding of application architecture"
        ],
        "weaknesses": [
            "Could deepen knowledge in complex edge cases and optimization strategies",
            "Explore advanced framework features and performance tuning"
        ],
        "topics_to_improve": [
            "System Optimization & Edge Cases",
            "Domain Framework Deep Dives",
            "Architecture Trade-offs & Concurrency"
        ],
        "recommended_resources": [
            {"title": "Official Language & Framework Documentation", "url": "https://docs.python.org/3/"},
            {"title": "Interactive System Architecture & Design Guides", "url": "https://refactoring.guru/"},
            {"title": "LeetCode & System Design Technical Practice", "url": "https://leetcode.com/"}
        ],
        "interview_summary": f"The candidate completed the interview session with an overall performance score of {overall_score}/10. Displays technical potential suitable for target company hiring benchmarks."
    }
