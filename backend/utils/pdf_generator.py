import os
import json
import logging
from typing import Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)

logger = logging.getLogger(__name__)

def generate_pdf_report(
    output_pdf_path: str,
    candidate_name: str,
    company: str,
    role: str,
    overall_score: float,
    scores_breakdown: Dict[str, float],
    strengths: List[str],
    weaknesses: List[str],
    topics_to_improve: List[str],
    recommended_resources: List[Dict[str, str]],
    interview_summary: str,
    questions_history: List[Dict[str, Any]]
) -> str:
    """
    Generate a professional, placement-ready PDF candidate evaluation report using ReportLab.
    """
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#1E293B")      # Dark Slate
    SECONDARY = colors.HexColor("#2563EB")    # Royal Blue
    ACCENT = colors.HexColor("#0D9488")       # Teal
    BG_LIGHT = colors.HexColor("#F8FAFC")     # Soft Grey
    TEXT_DARK = colors.HexColor("#334155")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=PRIMARY,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        textColor=SECONDARY,
        spaceAfter=15
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=PRIMARY,
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=TEXT_DARK,
        leading=14
    )
    bold_body_style = ParagraphStyle(
        'BoldBodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=TEXT_DARK,
        leading=14
    )

    story = []

    # Title Banner
    story.append(Paragraph("AI INTERVIEW ASSISTANT", title_style))
    story.append(Paragraph(f"Candidate Performance Evaluation Report • {company} ({role})", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=SECONDARY, spaceAfter=15))

    # Candidate Meta Details Header Box
    meta_data = [
        [Paragraph("<b>Candidate Name:</b>", body_style), Paragraph(candidate_name, body_style),
         Paragraph("<b>Target Company:</b>", body_style), Paragraph(company, body_style)],
        [Paragraph("<b>Target Role:</b>", body_style), Paragraph(role, body_style),
         Paragraph("<b>Overall Score:</b>", bold_body_style), Paragraph(f"<b>{overall_score} / 10.0</b>", bold_body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[110, 160, 110, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # Domain Scores Table
    story.append(Paragraph("Domain Score Breakdown", heading_style))
    scores_data = [
        [Paragraph("<b>Domain Topic</b>", bold_body_style), Paragraph("<b>Score (0-10)</b>", bold_body_style), Paragraph("<b>Performance Rating</b>", bold_body_style)]
    ]
    for domain, score in scores_breakdown.items():
        rating = "Excellent" if score >= 8 else "Good" if score >= 6 else "Needs Improvement"
        scores_data.append([
            Paragraph(domain, body_style),
            Paragraph(f"{score:.1f}", body_style),
            Paragraph(rating, body_style)
        ])

    scores_table = Table(scores_data, colWidths=[200, 140, 200])
    scores_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(scores_table)
    story.append(Spacer(1, 15))

    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(interview_summary, body_style))
    story.append(Spacer(1, 15))

    # Key Strengths & Areas to Improve
    story.append(Paragraph("Key Strengths", heading_style))
    for s in strengths:
        story.append(Paragraph(f"• {s}", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Areas to Improve & Recommended Resources", heading_style))
    for w in weaknesses:
        story.append(Paragraph(f"• {w}", body_style))
    story.append(Spacer(1, 8))
    
    for res in recommended_resources:
        title = res.get("title", "Resource")
        url = res.get("url", "")
        story.append(Paragraph(f"  🔗 <b>{title}</b>: {url}", body_style))
    
    story.append(Spacer(1, 15))
    story.append(PageBreak())

    # Detailed Question History Section
    story.append(Paragraph("Detailed Question & Answer Transcript", heading_style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=15))

    for idx, item in enumerate(questions_history, 1):
        q = item.get("question", {})
        a = item.get("answer", {})
        
        # Support both ORM objects and dicts
        if hasattr(q, 'question_text'):
            q_text = q.question_text or ""
            topic = q.topic or "General"
        else:
            q_text = q.get("question_text", "") if q else ""
            topic = q.get("topic", "General") if q else "General"

        if hasattr(a, 'user_answer'):
            user_ans = a.user_answer if a else "No Answer"
            score = a.total_score if a else 0.0
            feedback = a.feedback if a else ""
            best_ans = a.best_answer if a else ""
        else:
            user_ans = a.get("user_answer", "No Answer") if a else "No Answer"
            score = a.get("total_score", 0.0) if a else 0.0
            feedback = a.get("feedback", "") if a else ""
            best_ans = a.get("best_answer", "") if a else ""

        story.append(Paragraph(f"<b>Q{idx} [{topic}] - Score: {score}/10</b>", heading_style))
        story.append(Paragraph(f"<b>Question:</b> {q_text}", body_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>Candidate Answer:</b> {user_ans}", body_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>Feedback:</b> {feedback}", body_style))
        if best_ans:
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"<b>Model Answer:</b> {best_ans}", body_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=10, spaceAfter=10))

    # Build PDF
    doc.build(story)
    logger.info(f"PDF report generated at: {output_pdf_path}")
    return output_pdf_path
