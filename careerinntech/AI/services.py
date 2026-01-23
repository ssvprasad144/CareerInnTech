import json
import logging
from openai import OpenAI
from django.conf import settings
from .models import InterviewMessage
from .telemetry import log_api_call

# =========================
# OpenAI Client
# =========================
client = OpenAI(api_key=settings.OPENAI_API_KEY)
logger = logging.getLogger(__name__)

# =========================
# Utility: Answer Summarizer
# =========================
def summarize_answer(text):
    """Produce a one-line summary for an answer using a cheaper model."""
    try:
        prompt = (
            "Summarize the following candidate answer in one concise sentence:\n\n"
            + text
        )

        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=60
        )

        try:
            log_api_call(
                "chat",
                model="gpt-3.5-turbo",
                prompt_text=prompt,
                response=resp,
                extra={"purpose": "answer_summary"}
            )
        except Exception:
            pass

        return resp.choices[0].message.content.strip()

    except Exception:
        return ""


# =========================
# Feedback Parsing
# =========================
def parse_feedback_raw(raw, weights, qa_pairs, conversation=""):
    """Parse raw LLM feedback text into a normalized data dict."""

    def _extract_json(text):
        try:
            return json.loads(text)
        except Exception:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start:end + 1])
                except Exception:
                    return None
            return None

    data = _extract_json(raw)
    if data is None:
        return None

    # -------------------------
    # Skill score normalization
    # -------------------------
    skill_scores = {}
    for s in data.get("skills", []):
        name = s.get("name")
        val = s.get("score", 0)
        try:
            skill_scores[name] = float(val)
        except Exception:
            try:
                skill_scores[name] = float(str(val).strip())
            except Exception:
                skill_scores[name] = 0.0

    weighted_score = 0.0
    for k, v in weights.items():
        weighted_score += skill_scores.get(k, 0) * v

    # Detect 0–10 scale and normalize to 100
    try:
        max_skill = max(skill_scores.values()) if skill_scores else 0
    except Exception:
        max_skill = 0

    if max_skill <= 10:
        weighted_score *= 10.0

    weighted_score = max(0.0, min(weighted_score, 100.0))
    data["overall_score"] = round(weighted_score)

    data["score_breakdown"] = {
        k: skill_scores.get(k, 0) for k in weights
    }

    data["ui_summary"] = (
        "Your overall score is "
        + str(data["overall_score"])
        + " out of 100."
    )

    data["raw_llm"] = raw

    # -------------------------
    # Fluency / Clarity fallback
    # -------------------------
    fluency = data.get("fluency")
    clarity = data.get("clarity")

    if fluency is None:
        fluency = int(skill_scores.get("Communication", 0))
    if clarity is None:
        clarity = int(skill_scores.get("Communication", 0))

    data["fluency"] = int(fluency)
    data["clarity"] = int(clarity)

    # -------------------------
    # Match per-question feedback
    # -------------------------
    def normalize(text):
        if not text:
            return ""
        return " ".join(str(text).lower().split())

    llm_list = data.get("per_question_feedback", []) or []
    llm_by_q = {}

    for f in llm_list:
        qnorm = normalize(f.get("question", ""))
        if qnorm and qnorm not in llm_by_q:
            llm_by_q[qnorm] = f

    full_feedback = []

    for pair in qa_pairs:
        q = pair.get("question", "")
        a = pair.get("answer", "")
        qnorm = normalize(q)

        matched = None
        if qnorm in llm_by_q:
            matched = llm_by_q[qnorm]
        else:
            for k, v in llm_by_q.items():
                if qnorm and (qnorm in k or k in qnorm):
                    matched = v
                    break

        if matched:
            full_feedback.append({
                "question": matched.get("question", q),
                "answer": matched.get("answer", a),
                "feedback": matched.get("feedback", "No feedback generated."),
                "score": matched.get("score", 0)
            })
        else:
            fb = (
                "Answer was skipped or too short. "
                "Try to provide a more complete response."
                if a.upper() == "SKIPPED" or len(a) < 5
                else "No feedback generated."
            )
            full_feedback.append({
                "question": q,
                "answer": a,
                "feedback": fb,
                "score": 0
            })

    data["per_question_feedback"] = full_feedback
    return data


# =========================
# Interview System Prompts
# =========================
SYSTEM_PROMPTS = {
    "web": "You are a senior web developer conducting a technical interview.",
    "aiml": "You are an AI/ML engineer conducting a technical interview.",
    "analyst": "You are a data analyst interviewer.",
    "hr": "You are an HR interviewer assessing communication and behavior."
}


# =========================
# Interview Question Engine
# =========================
def get_ai_response(interview_type, conversation, config=None):
    config = config or {}

    role = config.get("role") or interview_type
    branch = config.get("branch")
    difficulty = config.get("difficulty") or "standard"
    stack = config.get("stack") or []
    duration_minutes = config.get("duration_minutes") or "15"
    question_index = config.get("question_index") or 1
    total_questions = config.get("total_questions") or 10
    interviewer_style = config.get("interviewer_style") or "balanced"
    warmup_active = config.get("warmup_active") or False
    answer_quality = config.get("answer_quality") or "medium"
    focus_dsa = config.get("focus_dsa") or 40
    focus_system = config.get("focus_system_design") or 35
    focus_behavioral = config.get("focus_behavioral") or 25

    system_prompt = (
        "You are an AI interviewer.\n\n"
        "Rules:\n"
        "- YOU ask the interview questions.\n"
        "- The user only answers.\n"
        "- Ask one question at a time.\n\n"
        "Context:\n"
        "Role: " + str(role) + "\n"
        "Branch: " + str(branch) + "\n"
        "Stack: " + (", ".join(stack) if stack else "General") + "\n"
        "Difficulty: " + difficulty + "\n"
        "Question " + str(question_index) + " of " + str(total_questions)
    )

    messages = [{"role": "system", "content": system_prompt}]

    for msg in conversation:
        messages.append({
            "role": "user" if msg["sender"] == "user" else "assistant",
            "content": msg["message"]
        })

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.25,
        max_tokens=200
    )

    try:
        log_api_call("chat", model="gpt-3.5-turbo", prompt_text=system_prompt, response=response)
    except Exception:
        pass

    return response.choices[0].message.content.strip()


# =========================
# Feedback Generator (FIXED)
# =========================
def generate_feedback(session):

    SKILL_WEIGHTS = {
        "Technical Knowledge": 0.28,
        "Problem Solving": 0.28,
        "Communication": 0.14,
        "Confidence": 0.14,
        "Creativity": 0.08,
        "Time Management": 0.08
    }

    messages = InterviewMessage.objects.filter(
        session=session
    ).order_by("created_at")

    conversation = ""
    attempted_answers = 0
    qa_pairs = []
    per_question_feedback = []
    last_ai_msg = ""

    for msg in messages:
        role = "Candidate" if msg.sender == "user" else "Interviewer"
        conversation += role + ": " + msg.message + "\n"

        if msg.sender == "ai":
            last_ai_msg = msg.message
        elif msg.sender == "user":
            attempted_answers += 1
            answer = msg.message.strip() if msg.message else ""
            qa_pairs.append({
                "question": last_ai_msg,
                "answer": answer
            })

    # -------------------------
    # SAFE QA TEXT BUILD
    # -------------------------
    qa_text = ""
    for i, qa in enumerate(qa_pairs):
        qa_text += (
            str(i + 1) + ". Q: " + qa["question"] + "\n"
            "   A: " + qa["answer"] + "\n"
        )

    prompt = (
        "Return STRICT JSON only.\n\n"
        "Interview Type: " + str(getattr(session, "interview_type", "N/A")) + "\n"
        "Answers Attempted: " + str(attempted_answers) + "\n\n"
        "QA Pairs:\n"
        + qa_text +
        "\nConversation:\n"
        + conversation
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Return STRICT JSON. No explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.25,
            max_tokens=1000
        )

        raw = response.choices[0].message.content
        data = parse_feedback_raw(raw, SKILL_WEIGHTS, qa_pairs, conversation)

        if data is None:
            return json.dumps({"overall_score": 0, "raw_llm": raw})

        return json.dumps(data)

    except Exception as e:
        logger.exception("generate_feedback failed: %s", e)
        return json.dumps({"overall_score": 0})


# =========================
# Rephrase Question
# =========================
def rephrase_question(question):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Rephrase clearly in one sentence."},
                {"role": "user", "content": question}
            ],
            temperature=0.25,
            max_tokens=48
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return question


# =========================
# Hint Generator
# =========================
def generate_hint(question, context=None):
    context = context or {}
    role = context.get("role") or ""
    stack = context.get("stack") or []

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Give a short helpful hint."},
                {
                    "role": "user",
                    "content": (
                        "Question: " + question +
                        "\nRole: " + role +
                        "\nStack: " + (", ".join(stack) if stack else "General")
                    )
                }
            ],
            temperature=0.35,
            max_tokens=60
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Focus on the core concept and explain your approach."
