# 🎙️ AI Interview Assistant - Enterprise Candidate Placement Platform

An enterprise-grade, production-quality AI Interview Assistant built with **FastAPI**, **Streamlit**, **SQLAlchemy ORM**, **SQLite**, and **Google Gemini API**. 

Tailored specifically for candidates preparing for placements in top tech companies like **Cognizant, Accenture, Deloitte, Capgemini, Infosys, TCS Digital, and Wipro**.

---

## 🌟 Key Features

1. **Authentication & Session Security**
   - Candidate registration, secure login, password hashing with `bcrypt`, and stateless `JWT` session tokens.

2. **PDF Resume Parser & Extractor**
   - Upload PDF resumes to automatically extract technical skills (50+ keyword taxonomy), education, projects, and work experience using PyPDF/pdfplumber algorithms.

3. **Enterprise Interview Setup**
   - Customize interview parameters:
     - **Company**: Cognizant, Accenture, Infosys, TCS, Capgemini, Deloitte, Wipro.
     - **Role**: Python Developer, Data Analyst, Data Scientist, Java Developer, Full Stack Developer.
     - **Difficulty**: Easy, Medium, Hard.
     - **Interview Type**: Technical, HR, Mixed.
     - **Question Count**: 5, 10, or 15 questions.

4. **Dynamic & Adaptive AI Interviewer (Google Gemini LLM)**
   - Tailored non-repeating question generation using candidate resume, target company hiring standards, and role requirements.
   - Dynamic adaptive difficulty adjustment:
     - High score (≥ 8.0/10) ➔ Increases technical complexity and architectural depth.
     - Low score (≤ 4.0/10) ➔ Asks foundational clarifying follow-up questions.

5. **0-10 Answer Evaluation Engine**
   - Evaluates every response across 5 core metrics: **Correctness, Completeness, Technical Accuracy, Communication, and Confidence**.
   - Provides 10/10 Model Answers, missing concepts, and actionable feedback.

6. **Automated Report Generation & Downloadable PDF Certificates**
   - Generates placement-ready PDF evaluation reports using `ReportLab`. Includes domain score breakdown (Python, SQL, DBMS, OOP, Communication), executive summary, strengths, weaknesses, recommended resources, and complete Q&A transcript.

7. **Interactive Dashboard & Analytics**
   - Plotly progress graphs over time, domain score bar charts, skill radar charts, weak/strong topic pills, past interview search & filtering, and top candidate leaderboard rankings.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend Framework** | FastAPI (Python 3.11+) |
| **Frontend UI** | Streamlit + Custom Glassmorphism CSS |
| **Database & ORM** | SQLite + SQLAlchemy 2.0 ORM |
| **LLM Engine** | Google Gemini API (`gemini-1.5-flash`) |
| **PDF Processing** | PyPDF, pdfplumber & ReportLab |
| **Data Viz** | Plotly & Pandas |
| **Security** | Passlib (Bcrypt) & Python-Jose (JWT) |

---

## 🏗️ Project Architecture

```
cherrypro/
├── backend/
│   ├── main.py                  # FastAPI Application & Router Registration
│   ├── config.py                # Environment Configuration Settings
│   ├── database/
│   │   ├── connection.py        # SQLAlchemy Engine & Session Generator
│   ├── models/                  # SQLAlchemy ORM Models & Pydantic Schemas
│   │   ├── user.py, resume.py, interview.py, question.py, answer.py, report.py, analytics.py, schemas.py
│   ├── routers/                 # API Endpoint Controllers
│   │   ├── auth.py, resume.py, interview.py, report.py, analytics.py
│   ├── services/                # Business Logic & Core Workflows
│   │   ├── auth_service.py, resume_service.py, interview_service.py, gemini_service.py, report_service.py, analytics_service.py
│   ├── utils/                   # Security, PDF Generation, Resume Parsing
│   │   ├── security.py, pdf_generator.py, resume_parser.py
│   ├── prompts/                 # Gemini Prompt Templates
│   │   ├── question_prompts.py, evaluation_prompts.py, report_prompts.py
│   └── static/uploads/          # Resumes & PDF Reports Storage
├── frontend/
│   ├── app.py                   # Streamlit Main App & Router
│   ├── config.py                # App Options & Backend URL
│   ├── utils/                   # Custom CSS Styles, Session Helper, API Client
│   └── components/              # Page UI Components
│       ├── auth.py, dashboard.py, resume_upload.py, interview_setup.py, interview_room.py, report_view.py, leaderboard.py
├── tests/                       # Automated Pytest Suite
│   ├── conftest.py, test_auth.py, test_interview.py, test_report_analytics.py
├── .env.example                 # Environment Template
├── .gitignore                   # Git Ignore Rules
└── requirements.txt             # Project Dependencies
```

---

## 🚀 Quickstart Guide

### 1. Environment Setup

Clone repository and create a Python virtual environment:
```bash
py -3.11 -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate # Linux/Mac
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` file from template:
```bash
cp .env.example .env
```

Add your **Google Gemini API Key** in `.env`:
```env
GEMINI_API_KEY="your_actual_gemini_api_key_here"
```
*(Note: If `GEMINI_API_KEY` is not provided, the application runs in Intelligent Mock Mode without crashing).*

### 3. Launch Backend API Server

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
- API Documentation (Swagger UI): `http://127.0.0.1:8000/docs`

### 4. Launch Streamlit Frontend UI

In a new terminal window:
```bash
streamlit run frontend/app.py --server.port 8501
```
- Streamlit Web App: `http://127.0.0.1:8501`

---

## 🧪 Automated Testing

Run unit and integration test suite:
```bash
pytest
```

---

## 📄 Resume Highlight Bullet Points (For Placement Resumes)

- **AI Interview Assistant (FastAPI, Streamlit, Google Gemini API, SQLAlchemy)**
  - Engineered an enterprise-grade AI mock interview platform featuring PDF resume extraction, adaptive question generation, dynamic 0-10 answer scoring, and automated placement PDF evaluation report generation.
  - Implemented clean architecture using FastAPI backend, SQLite database with SQLAlchemy ORM, and JWT authentication.
  - Integrated Google Gemini LLM with prompt templates for dynamic, non-repeating questions aligned with Cognizant, Accenture, Deloitte, TCS, and Infosys hiring benchmarks.
  - Designed responsive Streamlit UI with glassmorphism aesthetics, dark/light mode themes, Plotly analytics, and candidate leaderboard.
