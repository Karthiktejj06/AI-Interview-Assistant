"""
Prompt templates for generating interview questions using Google Gemini API.
"""

QUESTION_GENERATION_PROMPT = """
You are an expert Senior Engineering Manager and Technical Recruiter conducting an interview at {company} for the role of {role}.

Candidate Context:
- Target Company: {company} (Tailor style to company's typical hiring standards)
- Target Role: {role}
- Difficulty Level: {difficulty}
- Interview Type: {interview_type} (Technical, HR, or Mixed)
- Previously Asked Questions (DO NOT REPEAT):
{previous_questions}

Candidate Resume Summary:
- Parsed Skills: {skills}
- Key Projects: {projects}
- Education: {education}
- Experience: {experience}

Adaptive Guidance:
{adaptive_instruction}

CRITICAL ROLE-SPECIFIC MANDATES:
1. Generate EXACTLY ONE high-quality, professional interview question tailored SPECIFICALLY to the target role '{role}', company, difficulty level, and candidate background.
2. STRICT DOMAIN RELEVANCE:
   - If {role} is "Java Developer", ask about Java/JVM/Spring Boot/Multithreading/OOP in Java.
   - If {role} is "Data Analyst", ask about SQL/Pandas/Data Analytics/KPIs/Data Cleaning.
   - If {role} is "Data Scientist", ask about Machine Learning/Statistics/Model Evaluation/Feature Engineering.
   - If {role} is "Frontend Developer", ask about JavaScript/React/CSS/DOM/Web Performance.
   - If {role} is "Full Stack Developer", ask about REST APIs/Database Design/Frontend-Backend Integration.
   - If {role} is "DevOps / Cloud Engineer", ask about Docker/Kubernetes/CI-CD/Terraform/Cloud Monitoring.
   - If {role} is "QA / Automation Engineer", ask about Test Frameworks/Selenium/API Testing/Boundary Analysis.
   - If {role} is "HR / Behavioral", ask about leadership, conflict resolution, project failure post-mortems, or teamwork.
   - DO NOT ask generic Python/SQL questions unless they are core to the target role '{role}'.
3. The question MUST NOT repeat or closely resemble any of the previously asked questions.
4. Identify the primary technical/hr topic of this question.
5. List 3 to 5 key expected concepts or keywords that a top-tier candidate's answer should contain.

OUTPUT FORMAT:
Respond ONLY with a valid JSON object matching the following structure (no markdown fences, no raw text around it):
{{
  "question_text": "The exact wording of the question to ask the candidate",
  "topic": "Primary Topic",
  "difficulty": "{difficulty}",
  "expected_concepts": ["concept1", "concept2", "concept3"]
}}
"""

ADAPTIVE_INCREASE_DIFFICULTY = "The candidate answered the previous question exceptionally well. Increase the technical depth, complexity, or ask a deeper architectural/optimization follow-up question."
ADAPTIVE_EASIER_FOLLOWUP = "The candidate struggled with the previous question. Ask a clearer, foundational follow-up question to assess basic understanding of core principles."
ADAPTIVE_NEUTRAL = "Maintain standard difficulty progression and explore another key technical domain required for this role."

