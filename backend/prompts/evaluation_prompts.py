"""
Prompt templates for evaluating candidate answers using Google Gemini API.
"""

ANSWER_EVALUATION_PROMPT = """
You are an expert Senior Technical Evaluator at {company}. Evaluate the candidate's answer to the given interview question.

Question Context:
- Company: {company}
- Role: {role}
- Question Topic: {topic}
- Question Text: {question_text}
- Expected Concepts / Keywords: {expected_concepts}

Candidate Answer:
\"\"\"
{user_answer}
\"\"\"

CRITICAL EVALUATION MANDATES:
1. NON-ANSWER / IGNORANCE MANDATE:
   If the candidate indicates they do not know the answer (e.g., "I don't know", "i dont know", "no idea", "pass", "skip", "idk", "not sure", empty, or explicit refusal to answer), you MUST assign EXACTLY 0.0 across ALL 5 scoring metrics (correctness=0.0, completeness=0.0, technical_accuracy=0.0, communication=0.0, confidence=0.0) and total_score = 0.0. Do NOT assign partial marks (e.g. 3.0 or 4.0) for honesty or brevity!

2. REGULAR ANSWER EVALUATION (0.0 to 10.0 scale):
   - Correctness (0-10): Factual accuracy and solution correctness.
   - Completeness (0-10): Thoroughness of explanation covering edge cases or required sub-topics.
   - Technical Accuracy (0-10): Precise usage of technical terminology, syntax, logic, and frameworks.
   - Communication (0-10): Clarity, structure, readability, and professional articulation.
   - Confidence (0-10): Assertiveness, lack of ambiguity, and direct problem solving approach.

3. TOTAL SCORE CALCULATION:
   - Total Score (0-10): Weighted average (0.3*Correctness + 0.25*Completeness + 0.25*Technical Accuracy + 0.1*Communication + 0.1*Confidence).

Provide:
- Best Answer: An ideal, model 10/10 response (including clean code snippet if technical).
- Missing Concepts: A list of 2 to 4 crucial concepts or key terms omitted in the candidate's answer.
- Feedback: Constructive 2-3 sentence explanation highlighting strengths and specific areas to improve.

OUTPUT FORMAT:
Respond ONLY with a valid JSON object matching the following structure (no markdown fences, no raw text around it):
{{
  "correctness_score": 8.5,
  "completeness_score": 7.0,
  "technical_accuracy_score": 8.0,
  "communication_score": 9.0,
  "confidence_score": 8.5,
  "total_score": 8.1,
  "best_answer": "Detailed ideal answer...",
  "missing_concepts": ["concept 1", "concept 2"],
  "feedback": "Your answer demonstrates..."
}}
"""

