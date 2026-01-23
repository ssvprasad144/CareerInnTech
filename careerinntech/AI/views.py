from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import InterviewSession, InterviewMessage
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import textwrap
from .services import generate_feedback
import tempfile
import json
from openai import OpenAI
def interview_preparation(request):
    """
    AI Interview preparation landing page
    """
    return render(request, 'ai/interview_preparation.html')


@login_required
def interview_types(request):
    return render(request, "ai/interview_types.html")


@login_required
def interview_tips(request):
    return render(request, "ai/interview_tips.html")


@login_required
def interview_myths(request):
    return render(request, "ai/interview_myths.html")


@login_required
def interview_question_bank(request):
    return render(request, "ai/interview_question_bank.html")


@login_required
def interview_resume_prep(request):
    return render(request, "ai/interview_resume_prep.html")


@login_required
def interview_communication(request):
    return render(request, "ai/interview_communication.html")

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# ---------------- LANDING ----------------
@login_required
def ai_mock_interview_landing(request):
    if not request.user.is_staff:
        return render(request, "ai/not_authorized.html", status=403)
    return render(request, "ai/ai_mock_interview.html")

@login_required
def ai_interview_select(request):
    if not request.user.is_staff:
        return render(request, "ai/not_authorized.html", status=403)
    return render(request, "ai/ai_interview_select.html")

def interview_config(request, interview_type):
    return redirect("ai-interview-select")

# ---------------- START ----------------
from core.models import StudentProfile  # or correct app

@login_required
@require_POST
def start_interview(request):
    interview_type = request.POST.get("interview_type")
    interview_mode = request.POST.get("interview_mode") or "voice"
    interview_difficulty = request.POST.get("difficulty")
    interview_stack = request.POST.getlist("stack")
    interview_branch = request.POST.get("branch")
    interview_role = request.POST.get("role")
    duration_minutes = request.POST.get("duration_minutes") or "15"
    question_count = request.POST.get("question_count") or "10"
    # Focus areas removed from UI — no client-provided focus values
    interviewer_style = request.POST.get("interviewer_style") or "balanced"
    warmup = request.POST.get("warmup") in ["1", "on", "true", True]

    session = InterviewSession.objects.create(
        user=request.user if request.user.is_authenticated else None,
        interview_type=interview_type
    )

    request.session["interview_session_id"] = session.id
    request.session["interview_mode"] = interview_mode
    request.session["interview_type"] = interview_type
    request.session["interview_difficulty"] = interview_difficulty
    request.session["interview_stack"] = interview_stack
    request.session["interview_branch"] = interview_branch
    request.session["interview_role"] = interview_role
    request.session["duration_minutes"] = duration_minutes
    request.session["question_count"] = question_count
    # focus values intentionally not stored in session
    request.session["interviewer_style"] = interviewer_style
    request.session["warmup"] = warmup

    return redirect("ai-interview-live")

# ---------------- LIVE ----------------
@login_required
def ai_interview_live(request):
    session_id = request.session.get("interview_session_id")
    if not session_id:
        return redirect("ai-mock-interview")

    if not request.user.is_staff:
        return render(request, "ai/not_authorized.html", status=403)

    # ✅ Dynamic user name
    if request.user.is_authenticated:
        user_name = (
            request.user.first_name
            or request.user.username
            or "Candidate"
        )
    else:
        user_name = "Candidate"

    return render(request, "ai/interview_live.html", {
        "session_id": session_id,
        "user_name": user_name,
        "interview_type": request.session.get("interview_type"),
        "interview_mode": request.session.get("interview_mode"),
        "interview_difficulty": request.session.get("interview_difficulty"),
        "interview_stack": request.session.get("interview_stack", []),
        "interview_role": request.session.get("interview_role"),
        "interview_branch": request.session.get("interview_branch"),
        "duration_minutes": request.session.get("duration_minutes", "15"),
        "question_count": request.session.get("question_count", "10"),
        # Focus areas removed from selection; voice flow will use defaults if needed
        "interviewer_style": request.session.get("interviewer_style", "balanced"),
        "warmup": request.session.get("warmup", False),
    })

# ---------------- STT ----------------
@login_required
@csrf_exempt
@require_POST
def stt_transcribe(request):
    audio = request.FILES.get("audio")
    if not audio:
        return JsonResponse({"error": "No audio"}, status=400)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        for chunk in audio.chunks():
            tmp.write(chunk)
        path = tmp.name

    with open(path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )

    # Telemetry: log transcription call
    try:
        from .telemetry import log_api_call
        log_api_call("transcription", model="whisper-1", prompt_text=None, response=transcript)
    except Exception:
        pass

    return JsonResponse({"text": transcript.text})

# ---------------- FINISH ----------------
import json
from .services import generate_feedback

@login_required
@csrf_exempt
@require_POST
def finish_interview(request):
    data = json.loads(request.body)
    session_id = data.get("session_id")
    speech_metrics = data.get("speech_metrics") or {}
    face_metrics = data.get("face_metrics") or {}
    transcripts = data.get("transcripts") or []

    session = InterviewSession.objects.get(id=session_id)

    ai_response = generate_feedback(session)

    try:
        feedback_data = json.loads(ai_response)
    except json.JSONDecodeError:
        feedback_data = {}

    request.session["feedback_data"] = feedback_data
    request.session["speech_metrics"] = speech_metrics
    request.session["face_metrics"] = face_metrics
    request.session["transcripts"] = transcripts

    return JsonResponse({
        "redirect": f"/ai/feedback/{session_id}/"
    })

# ---------------- FEEDBACK ----------------
@login_required
def interview_feedback_page(request, session_id):
    feedback = request.session.get("feedback_data", {})
    speech_metrics = request.session.get("speech_metrics", {})
    face_metrics = request.session.get("face_metrics", {})

    return render(request, "ai/interview_feedback.html", {
        "session_id": session_id,
        "overall_score": feedback.get("overall_score"),
        "verdict_title": feedback.get("verdict_title"),
        "verdict_summary": feedback.get("verdict_summary"),
        "skills": feedback.get("skills", []),
        "strengths": feedback.get("strengths", []),
        "improvements": feedback.get("improvements", []),
        "final_verdict": feedback.get("final_verdict"),
        "feedback": feedback.get("detailed_feedback"),
        "speech_metrics": speech_metrics,
        "face_metrics": face_metrics,
    })



def _build_question_answer_pairs(session):
    messages = InterviewMessage.objects.filter(session=session).order_by("created_at")
    pairs = []
    current_question = None
    current_answer_parts = []

    for msg in messages:
        # Skip AI intro/welcome messages when building QA pairs
        if msg.sender == "ai":
            text_lower = (msg.message or "").lower()
            if "introduce yourself" in text_lower or text_lower.startswith("welcome to"):
                # skip intro messages
                continue
            if current_question is not None:
                pairs.append({
                    "question": current_question,
                    "answer": " ".join(current_answer_parts).strip() or "—"
                })
            current_question = msg.message
            current_answer_parts = []
        else:
            current_answer_parts.append(msg.message)

    if current_question is not None:
        pairs.append({
            "question": current_question,
            "answer": " ".join(current_answer_parts).strip() or "—"
        })

    return pairs


@login_required
def interview_feedback_details(request, session_id):
    session = InterviewSession.objects.get(id=session_id)
    feedback = request.session.get("feedback_data", {})
    qa_pairs = _build_question_answer_pairs(session)
    speech_metrics = request.session.get("speech_metrics", {})
    face_metrics = request.session.get("face_metrics", {})
    # Merge per-question feedback from LLM into qa_pairs so each question has feedback and score
    per_q_fb = feedback.get("per_question_feedback", []) or []

    def normalize(s):
        if not s:
            return ""
        return " ".join(str(s).lower().split())

    fb_by_q = {}
    for f in per_q_fb:
        qnorm = normalize(f.get("question", ""))
        if qnorm and qnorm not in fb_by_q:
            fb_by_q[qnorm] = f

    enriched = []
    for idx, pair in enumerate(qa_pairs):
        q = pair.get("question", "")
        a = pair.get("answer", "")
        qnorm = normalize(q)
        fb = None
        if qnorm and qnorm in fb_by_q:
            fb = fb_by_q[qnorm]
        elif idx < len(per_q_fb):
            # fallback to index-aligned feedback if provided by LLM
            fb = per_q_fb[idx]

        # Normalize score: LLM may return 0-10 or 0-100. Provide both representations.
        raw_score = 0
        if fb and isinstance(fb.get("score"), (int, float)):
            raw_score = fb.get("score")
        # If score looks like 0-100, convert to 0-10 scale
        if raw_score > 10:
            score_pct = int(round(raw_score))
            score_10 = round(raw_score / 10.0, 1)
        else:
            score_10 = round(raw_score, 1)
            score_pct = int(round(score_10 * 10))

        enriched.append({
            "question": q,
            "answer": a,
            "feedback": (fb.get("feedback") if fb else "No feedback available."),
            "score_raw": raw_score,
            "score_10": score_10,
            "score_pct": score_pct
        })

    return render(request, "ai/interview_feedback_details.html", {
        "session_id": session_id,
        "qa_pairs": enriched,
        "overall_score": feedback.get("overall_score"),
        "verdict_title": feedback.get("verdict_title"),
        "verdict_summary": feedback.get("verdict_summary"),
        "skills": feedback.get("skills", []),
        "strengths": feedback.get("strengths", []),
        "improvements": feedback.get("improvements", []),
        "final_verdict": feedback.get("final_verdict"),
        "feedback": feedback.get("detailed_feedback"),
        "speech_metrics": speech_metrics,
        "face_metrics": face_metrics,
    })


@login_required
def download_feedback_pdf(request, session_id):
    session = InterviewSession.objects.get(id=session_id)
    feedback = request.session.get("feedback_data", {})
    qa_pairs = _build_question_answer_pairs(session)
    speech_metrics = request.session.get("speech_metrics", {})
    face_metrics = request.session.get("face_metrics", {})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=feedback_{session_id}.pdf"

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 1 * inch

    def draw_heading(text):
        nonlocal y
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1 * inch, y, text)
        y -= 0.3 * inch

    def draw_paragraph(text, indent=0):
        nonlocal y
        c.setFont("Helvetica", 10)
        wrap_width = 95
        for line in textwrap.wrap(text or "", width=wrap_width):
            c.drawString(1 * inch + indent, y, line)
            y -= 0.18 * inch
            if y < 1 * inch:
                c.showPage()
                y = height - 1 * inch

    draw_heading("AI Interview Feedback")
    draw_paragraph(f"Session ID: {session_id}")
    draw_paragraph(f"Overall Score: {feedback.get('overall_score', '--')}%")
    draw_paragraph(f"Verdict: {feedback.get('verdict_title', 'Interview Completed')}")
    draw_paragraph(feedback.get("verdict_summary", ""))

    if speech_metrics:
        y -= 0.1 * inch
        draw_heading("Speech Analytics")
        draw_paragraph(f"Avg WPM: {speech_metrics.get('avg_wpm', '--')}")
        draw_paragraph(f"Filler Words: {speech_metrics.get('filler_count', '--')}")
        draw_paragraph(f"Clarity Score: {speech_metrics.get('clarity_score', '--')}%")
        draw_paragraph(f"Pacing: {speech_metrics.get('pace_label', '--')}")

    if face_metrics:
        y -= 0.1 * inch
        draw_heading("Camera Analytics")
        draw_paragraph(f"Face Presence: {face_metrics.get('presence_pct', '--')}%")
        draw_paragraph(f"Avg Face Size: {face_metrics.get('avg_face_size_pct', '--')}%")
        draw_paragraph(f"Times Away: {face_metrics.get('away_count', '--')}")
        draw_paragraph(f"Engagement: {face_metrics.get('expression_label', '--')}")

    y -= 0.2 * inch
    draw_heading("Question-wise Answers")
    for idx, pair in enumerate(qa_pairs, start=1):
        draw_paragraph(f"Q{idx}: {pair['question']}")
        draw_paragraph(f"A{idx}: {pair['answer']}", indent=12)
        y -= 0.1 * inch
        if y < 1 * inch:
            c.showPage()
            y = height - 1 * inch

    y -= 0.2 * inch
    draw_heading("Detailed Feedback")
    draw_paragraph(feedback.get("detailed_feedback", ""))
    draw_paragraph(f"Final Verdict: {feedback.get('final_verdict', '')}")

    c.showPage()
    c.save()
    return response




