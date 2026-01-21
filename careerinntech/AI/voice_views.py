import json
import os

from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from openai import OpenAI

from .models import InterviewSession, InterviewMessage
from .services import get_ai_response, generate_feedback, generate_hint, summarize_answer
from .telemetry import log_api_call
from .services import summarize_answer
from .interview_utils import INTRO_QUESTIONS, generate_tts

@login_required
@csrf_exempt
@require_POST
def voice_next_question(request):
    data = json.loads(request.body)
    session_id = data.get("session_id")
    user_text = data.get("text")

    session = InterviewSession.objects.get(id=session_id)

    intro_text = "Hi, welcome to CareerInnTech mock interview. Please introduce yourself briefly."
    question_count = int(request.session.get("question_count", 10))
    warmup_enabled = bool(request.session.get("warmup", False))
    warmup_count = 2 if warmup_enabled else 0
    total_questions = question_count + warmup_count

    # ================= INTRO =================
    if user_text == "__START__":
        InterviewMessage.objects.create(
            session=session,
            sender="ai",
            message=intro_text
        )

        audio_url = generate_tts(session.id, intro_text)

        return JsonResponse({
            "text": intro_text,
            "audio_url": audio_url,
            "phase": "intro",
            "question_index": 0,
            "total_questions": total_questions
        })

    # ================= SAVE USER ANSWER =================
    InterviewMessage.objects.create(
        session=session,
        sender="user",
        message=user_text
    )

    # Record STT source if provided for telemetry
    stt_source = data.get("stt_source") if isinstance(data, dict) else None
    try:
        log_api_call("stt_event", model=None, prompt_text=None, response=None, extra={"session_id": session_id, "stt_source": stt_source})
    except Exception:
        pass

    # Produce a one-line summary for the answer (cheap) and persist to a summary file
    try:
        summary = summarize_answer(user_text)
        # write to file under BASE_DIR/ai_summaries/session_{id}.json (append)
        try:
            base = settings.BASE_DIR
        except Exception:
            base = os.getcwd()
        summaries_dir = os.path.join(base, "ai_summaries")
        os.makedirs(summaries_dir, exist_ok=True)
        summary_path = os.path.join(summaries_dir, f"session_{session.id}.jsonl")
        with open(summary_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": int(__import__('time').time()), "summary": summary, "text_len": len(user_text)}) + "\n")
    except Exception:
        pass

    # ================= MAIN INTERVIEW =================
    conversation = list(
        session.messages.order_by("id").values("sender", "message")
    )

    ai_messages = session.messages.filter(sender="ai").exclude(message=intro_text).count()
    if ai_messages >= total_questions:
        closing_text = "Thanks for completing the interview. I will now generate your feedback."
        InterviewMessage.objects.create(
            session=session,
            sender="ai",
            message=closing_text
        )
        return JsonResponse({
            "text": closing_text,
            "audio_url": generate_tts(session.id, closing_text),
            "phase": "complete",
            "question_index": ai_messages,
            "total_questions": total_questions
        })

    last_answer = session.messages.filter(sender="user").order_by("id").last()
    last_answer_text = last_answer.message if last_answer else ""
    last_word_count = len(last_answer_text.split())
    if last_word_count >= 60:
        answer_quality = "strong"
    elif last_word_count >= 30:
        answer_quality = "medium"
    else:
        answer_quality = "weak"

    config = {
        "role": request.session.get("interview_role"),
        "branch": request.session.get("interview_branch"),
        "difficulty": request.session.get("interview_difficulty"),
        "stack": request.session.get("interview_stack", []),
        "duration_minutes": request.session.get("duration_minutes"),
        "question_index": ai_messages + 1,
        "total_questions": total_questions,
        "interviewer_style": request.session.get("interviewer_style"),
        "warmup_active": warmup_enabled and (ai_messages < warmup_count),
        "answer_quality": answer_quality,
        "focus_dsa": int(request.session.get("focus_dsa", 40)),
        "focus_system_design": int(request.session.get("focus_system_design", 35)),
        "focus_behavioral": int(request.session.get("focus_behavioral", 25)),
    }

    ai_question = get_ai_response(
        session.interview_type,
        conversation,
        config
    )

    # Mark one question as a programming/code-editor question (ensure at least one)
    use_code_editor = False
    q_index = ai_messages + 1
    # choose the 3rd question as programming question (simple heuristic)
    if q_index == 3:
        use_code_editor = True

    InterviewMessage.objects.create(
        session=session,
        sender="ai",
        message=ai_question
    )

    return JsonResponse({
        "text": ai_question,
        "audio_url": generate_tts(session.id, ai_question),
        "phase": "main",
        "question_index": ai_messages + 1,
        "total_questions": total_questions,
        "use_code_editor": use_code_editor
    })


@login_required
@csrf_exempt
@require_POST
def voice_hint(request):
    data = json.loads(request.body)
    session_id = data.get("session_id")
    text = data.get("text")

    # Fetch the session object
    try:
        session = InterviewSession.objects.get(id=session_id)
    except InterviewSession.DoesNotExist:
        return JsonResponse({"error": "Session not found"}, status=404)

    # If no text provided, use last AI message
    if not text:
        last_ai = session.messages.filter(sender="ai").order_by("id").last()
        text = last_ai.message if last_ai else ""

    context = {
        "role": request.session.get("interview_role"),
        "stack": request.session.get("interview_stack", [])
    }
    hint = generate_hint(text or "", context)

    # Extend reply time by 30 seconds for this session (pseudo-logic, adjust as needed)
    # Example: set a session variable or model field to track extra time
    request.session['extra_time_for_hint'] = 30

    return JsonResponse({
        "text": hint,
        "phase": "hint",
        "extra_time": 30  # Inform frontend to allow 30s more
    })

@login_required
@csrf_exempt
def submit_code(request):
    import json
    from .services import evaluate_code
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body)
        session_id = data.get("session_id")
        question_index = data.get("question_index")
        code = data.get("code")
        # TODO: Validate session/question
        result = evaluate_code(session_id, question_index, code)
        return JsonResponse({"message": result.get("message", "Code received."), "followup": result.get("followup")})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    if not text:
        last_ai = session.messages.filter(sender="ai").order_by("id").last()
        text = last_ai.message if last_ai else ""

    context = {
        "role": request.session.get("interview_role"),
        "stack": request.session.get("interview_stack", [])
    }
    hint = generate_hint(text or "", context)

    return JsonResponse({
        "text": hint,
        "phase": "hint"
    })


@login_required
@csrf_exempt
@require_POST
def voice_skip_question(request):
    data = json.loads(request.body)
    session_id = data.get("session_id")

    session = InterviewSession.objects.get(id=session_id)

    intro_text = "Welcome to your AI mock interview. Please introduce yourself briefly."
    question_count = int(request.session.get("question_count", 10))
    warmup_enabled = bool(request.session.get("warmup", False))
    warmup_count = 2 if warmup_enabled else 0
    total_questions = question_count + warmup_count

    ai_messages = session.messages.filter(sender="ai").exclude(message=intro_text).count()
    if ai_messages >= total_questions:
        closing_text = "Thanks for completing the interview. I will now generate your feedback."
        InterviewMessage.objects.create(
            session=session,
            sender="ai",
            message=closing_text
        )
        return JsonResponse({
            "text": closing_text,
            "audio_url": generate_tts(session.id, closing_text),
            "phase": "complete",
            "question_index": ai_messages,
            "total_questions": total_questions
        })

    InterviewMessage.objects.create(
        session=session,
        sender="user",
        message="SKIPPED"
    )

    conversation = list(
        session.messages.order_by("id").values("sender", "message")
    )

    config = {
        "role": request.session.get("interview_role"),
        "branch": request.session.get("interview_branch"),
        "difficulty": request.session.get("interview_difficulty"),
        "stack": request.session.get("interview_stack", []),
        "duration_minutes": request.session.get("duration_minutes"),
        "question_index": ai_messages + 1,
        "total_questions": total_questions,
        "interviewer_style": request.session.get("interviewer_style"),
        "warmup_active": warmup_enabled and (ai_messages < warmup_count),
        "answer_quality": "weak",
        "focus_dsa": int(request.session.get("focus_dsa", 40)),
        "focus_system_design": int(request.session.get("focus_system_design", 35)),
        "focus_behavioral": int(request.session.get("focus_behavioral", 25)),
    }

    ai_question = get_ai_response(
        session.interview_type,
        conversation,
        config
    )

    InterviewMessage.objects.create(
        session=session,
        sender="ai",
        message=ai_question
    )

    return JsonResponse({
        "text": ai_question,
        "audio_url": generate_tts(session.id, ai_question),
        "phase": "main",
        "question_index": ai_messages + 1,
        "total_questions": total_questions
    })
