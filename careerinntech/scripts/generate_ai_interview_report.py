from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import textwrap
import os

OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
os.makedirs(OUT_PATH, exist_ok=True)
OUT_FILE = os.path.join(OUT_PATH, 'AI_interview_report.pdf')

def draw_paragraph(c, text, x, y, wrap_width=95, leading=14):
    for line in textwrap.wrap(text or '', width=wrap_width):
        c.drawString(x, y, line)
        y -= leading
        if y < inch:
            c.showPage()
            y = A4[1] - inch
    return y

def build_report():
    c = canvas.Canvas(OUT_FILE, pagesize=A4)
    width, height = A4
    x = inch
    y = height - inch

    c.setFont("Helvetica-Bold", 18)
    c.drawString(x, y, "CareerInnTech — AI Interview Features & Market Comparison")
    y -= 0.4 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "1. Executive Summary")
    y -= 0.25 * inch
    c.setFont("Helvetica", 10)
    y = draw_paragraph(c, (
        "This document summarizes the AI mock-interview product implemented in this repository, "
        "lists its technical and UX features, and compares it to notable competitors in the Indian market. "
        "It highlights differentiators and recommended next steps."), x, y)
    y -= 0.2 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "2. Key Features (extracted from codebase)")
    y -= 0.25 * inch
    c.setFont("Helvetica", 10)

    features = [
        "AI-driven question generation using OpenAI (adaptive prompts)",
        "Speech-to-text transcription via Whisper (server-side)",
        "Text-to-speech playback + browser TTS fallback",
        "Live recording with silence detection and automatic answer capture",
        "Live speech analytics: WPM, filler-words, clarity, pacing",
        "Camera analytics: face presence, engagement, away detection",
        "Hints, text-only view, skip and extend controls",
        "Code editor drawer and code submission placeholder",
        "Per-question feedback generation via LLM with JSON parsing",
        "Downloadable PDF feedback with question-wise answers and analytics",
        "Session-based storage and detailed QA pair building",
        "Configurable interview metadata (role, stack, difficulty, focus distribution)",
        "Fallbacks and robust matching for LLM per-question feedback",
        "Debug logging for LLM raw output when parsing fails"
    ]

    for f in features:
        y = draw_paragraph(c, f"- {f}", x+6, y, wrap_width=100)
    y -= 0.2 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "3. Architecture & Files of Interest")
    y -= 0.25 * inch
    c.setFont("Helvetica", 10)
    files = [
        "careerinntech/AI/services.py — LLM prompts, feedback generation, hint/rephrase",
        "careerinntech/AI/views.py — interview lifecycle, STT endpoint, feedback endpoints, PDF generation",
        "careerinntech/AI/models.py — InterviewSession and InterviewMessage storage",
        "static/js/ai/interview_live.js — client: recording, TTS, STT calls, live UX and metrics",
        "templates/ai/interview_live.html — interview UI",
        "templates/ai/interview_feedback_details.html — QA view, per-question reveal",
        "static/css/ai/interview_feedback_details.css — feedback styles"
    ]
    for f in files:
        y = draw_paragraph(c, f"- {f}", x+6, y, wrap_width=100)
    y -= 0.2 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "4. UX Highlights")
    y -= 0.25 * inch
    c.setFont("Helvetica", 10)
    ux = [
        "One-click Start/Stop with clear AI avatar states (listening/speaking)",
        "Text-only modal for reading questions and hints",
        "Small per-question feedback reveal button (hidden by default)",
        "Live tips during answers to guide pace and clarity",
        "Camera gaze/toast warnings to encourage eye contact",
        "Downloadable detailed PDF report for candidates"
    ]
    for u in ux:
        y = draw_paragraph(c, f"- {u}", x+6, y, wrap_width=100)
    y -= 0.2 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "5. Competitor Snapshot (India)")
    y -= 0.25 * inch
    c.setFont("Helvetica", 10)
    comp = {
        "InterviewBit": "Structured mock assessments, large question bank, curated learning paths, instant reports; mainly practice-focused rather than live AI interviewer.",
        "InterviewBuddy": "Expert-led 1:1 mock interviews (human coaches) with recordings and scorecards; strong expert network and personalized coaching.",
        "Talview": "Enterprise-grade AI interviewing + proctoring (Ivy & Alvy agents), strong fraud detection and integrations for hiring teams.",
        "Mercer | Mettl": "End-to-end assessment suite with secure proctoring and robust enterprise integrations; focus on scalability and compliance.",
        "HackerRank": "Code-challenge platform with interview prep kits and coding assessments; strong for technical assessments and company-style practice."
    }
    for k, v in comp.items():
        y = draw_paragraph(c, f"{k}: {v}", x+6, y, wrap_width=100)
    y -= 0.2 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "6. How CareerInnTech Stands Out")
    y -= 0.25 * inch
    c.setFont("Helvetica", 10)
    outs = [
        "Hybrid AI + Productized UX: real-time AI interviewer with browser TTS, STT, plus rich live metrics (speech + camera) — closer to a realistic interview loop than static mocks.",
        "Per-question, actionable feedback generated by LLM and merged into question-answer pairs, with a hidden-by-default reveal for focused review.",
        "Integrated analytics (clarity, WPM, filler words, gaze) that combine behavioral signals with content scoring — adds behavioral coaching missing in many competitors.",
        "Downloadable PDF report generator triggers from the product flow, enabling shareable candidate artifacts for self-review or recruiter handoff.",
        "Open, extensible design (Django backend + modular services) — easier to integrate new LLMs, custom prompts, or enterprise hooks compared to closed SaaS competitors."
    ]
    for o in outs:
        y = draw_paragraph(c, f"- {o}", x+6, y, wrap_width=100)
    y -= 0.2 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "7. Recommendations & Next Steps")
    y -= 0.25 * inch
    c.setFont("Helvetica", 10)
    recs = [
        "Add explicit per-question indices in LLM prompts to make feedback matching deterministic.",
        "Persist raw LLM feedback responses for audit and analysis when parsing fails.",
        "Add demo-ready screenshots and short GIFs to the PDF for marketing usage.",
        "Consider an enterprise mode integrating Talview/Mettl-like proctoring for customers who need compliance.",
        "Run user testing with 20 candidates and capture common LLM mismatches to refine prompts." 
    ]
    for r in recs:
        y = draw_paragraph(c, f"- {r}", x+6, y, wrap_width=100)

    y -= 0.2 * inch
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, "Generated from repository files and market research on competitor sites (InterviewBit, InterviewBuddy, Talview, Mercer|Mettl, HackerRank).")

    c.showPage()
    c.save()
    print("Report written to:", OUT_FILE)

if __name__ == '__main__':
    build_report()
