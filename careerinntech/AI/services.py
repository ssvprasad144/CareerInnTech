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


def summarize_answer(text):
    """Produce a one-line summary for an answer using a cheaper model."""
    try:
        prompt = f"Summarize the following candidate answer in one concise sentence:\n\n{text}"
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=60
        )
        try:
            log_api_call("chat", model="gpt-3.5-turbo", prompt_text=prompt, response=resp, extra={"purpose": "answer_summary"})
        except Exception:
            pass
        return resp.choices[0].message.content.strip()
    except Exception:
        return ""


def parse_feedback_raw(raw, weights, qa_pairs, conversation=""):
    """Parse raw LLM feedback text into a normalized data dict.

    Returns a dict matching the generate_feedback output (not JSON-stringified).
    """
    def _extract_json(text):
        try:
            return json.loads(text)
        except Exception:
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start:end+1])
                except Exception:
                    return None
            return None

    data = _extract_json(raw)
    if data is None:
        return None

    # Parse skill scores robustly as floats (LLM may return strings or numbers)
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

    weighted_score = sum(skill_scores.get(k, 0) * v for k, v in weights.items())

    # Some LLM prompts return skill scores on a 0-10 scale while the UI expects 0-100.
    # Detect a 0-10 scale (max skill <= 10) and scale up to 0-100.
    try:
        max_skill = max(skill_scores.values()) if skill_scores else 0
    except Exception:
        max_skill = 0

    if max_skill <= 10:
        weighted_score = weighted_score * 10.0

    # Clamp to 0-100 and round
    weighted_score = max(0.0, min(weighted_score, 100.0))
    data["overall_score"] = round(weighted_score)
    data["score_breakdown"] = {k: skill_scores.get(k, 0) for k in weights}
    data["ui_summary"] = f"Your overall score is {data['overall_score']} out of 100."

    try:
        data["raw_llm"] = raw
    except Exception:
        pass

    try:
        fluency = data.get("fluency", None)
        clarity = data.get("clarity", None)
    except Exception:
        fluency = None
        clarity = None

    if fluency is None:
        fluency = int(skill_scores.get("Communication", 0))
    if clarity is None:
        clarity = int(skill_scores.get("Communication", 0))

    try:
        data["fluency"] = int(fluency)
        data["clarity"] = int(clarity)
    except Exception:
        data["fluency"] = fluency
        data["clarity"] = clarity

    def normalize(s):
        if not s:
            return ""
        return " ".join(str(s).lower().split())

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
        if qnorm and qnorm in llm_by_q:
            matched = llm_by_q[qnorm]
        else:
            for k, v in llm_by_q.items():
                if k and qnorm and (qnorm in k or k in qnorm):
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
            fb = "Answer was skipped or too short. Try to provide a more complete response." if a.upper() == "SKIPPED" or len(a) < 5 else "No feedback generated."
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
# AI Interview Question Generator
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
    focus_system_design = config.get("focus_system_design") or 35
    focus_behavioral = config.get("focus_behavioral") or 25

    messages = [
        {
            "role": "system",
            "content": f"""
You are an AI interviewer.

Rules:
- YOU ask the interview questions.
- The user is the candidate and only answers.
- Ignore greetings like "yes", "ok", "start".
- Always ask the NEXT interview question.
- Never ask the user to ask a question.
- Do NOT explain answers.
- Ask one question at a time.

Adaptive rules:
- If the last answer is brief or shallow, ask a follow-up.
- Increase difficulty after strong answers.
- Simplify if answers are weak.

Interview context:
Role: {role}
Branch: {branch}
Stack: {', '.join(stack) if stack else 'General'}
Difficulty: {difficulty}
Style: {interviewer_style}
Duration: {duration_minutes} minutes
Question {question_index} of {total_questions}
Warm-up: {warmup_active}
Last answer quality: {answer_quality}
Focus: DSA {focus_dsa}%, System {focus_system_design}%, Behavioral {focus_behavioral}%

Interview type: {interview_type}
"""
        }
    ]

    for msg in conversation:
        role_type = "user" if msg["sender"] == "user" else "assistant"
        messages.append({
            "role": role_type,
            "content": msg["message"]
        })

    # Use the more cost-stable `gpt-3.5-turbo` for question generation per request
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.25,
        max_tokens=200
    )

    # Telemetry: log this chat call
    try:
        prompt_text = "\n".join([m.get("content", "") for m in messages])
    except Exception:
        prompt_text = None
    try:
        log_api_call("chat", model="gpt-4o-mini", prompt_text=prompt_text, response=response)
    except Exception:
        pass

    return response.choices[0].message.content.strip()

# =========================
# Feedback Generator
# =========================
def generate_feedback(session):

    SKILL_WEIGHTS = {
        "default": {
            "Technical Knowledge": 0.28,
            "Problem Solving": 0.28,
            "Communication": 0.14,
            "Confidence": 0.14,
            "Creativity": 0.08,
            "Time Management": 0.08
        }
    }

    messages = InterviewMessage.objects.filter(session=session).order_by("created_at")

    conversation = ""
    attempted_answers = 0
    per_question_feedback = []
    qa_pairs = []
    last_ai_msg = None
    for msg in messages:
        role = "Candidate" if msg.sender == "user" else "Interviewer"
        conversation += f"{role}: {msg.message}\n"
        if msg.sender == "ai":
            last_ai_msg = msg.message
        elif msg.sender == "user":
            attempted_answers += 1
            answer = msg.message.strip() if msg.message else ""
            qa_pairs.append({
                "question": last_ai_msg or "",
                "answer": answer
            })
            if answer.upper() == "SKIPPED" or len(answer) < 5:
                per_question_feedback.append({
                    "question": last_ai_msg or "",
                    "answer": answer,
                    "feedback": "Answer was skipped or too short. Try to provide a more complete response.",
                    "score": 0
                })

    weights = SKILL_WEIGHTS["default"]

    prompt = f"""
You are a professional technical interviewer.

Return STRICT JSON in this format:

{{
  "overall_score": number,
  "verdict_title": string,
  "verdict_summary": string,
  "skills": [
    {{ "name": "Technical Knowledge", "score": number }},
    {{ "name": "Problem Solving", "score": number }},
    {{ "name": "Communication", "score": number }},
    {{ "name": "Confidence", "score": number }},
    {{ "name": "Creativity", "score": number }},
    {{ "name": "Time Management", "score": number }}
  ],
  "strengths": [string],
  "improvements": [string],
  "final_verdict": string,
  "detailed_feedback": string,
  "per_question_feedback": [
    {{
      "question": string,
      "answer": string,
      "feedback": string,
      "score": number
    }}
  ]
}}

Interview Type: {getattr(session, 'interview_type', 'N/A')}
Answers Attempted: {attempted_answers}

Below is a numbered list of question/answer pairs extracted from the interview. For each pair, provide concise per-question feedback and a numeric score (0-10). The `per_question_feedback` array in your JSON MUST be the same length and in the SAME ORDER as the list below. Use the exact question text when filling the `question` field.

QA Pairs:
{''.join([f"{i+1}. Q: {qa['question']}\n   A: {qa['answer']}\n" for i, qa in enumerate(qa_pairs)])}

Conversation:
{conversation}
"""

    try:
        # Use `gpt-3.5-turbo` with lower temperature for reliable, repeatable JSON output
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Return STRICT JSON exactly as requested. Do not include any extra commentary."}, {"role": "user", "content": prompt}],
            temperature=0.25,
            max_tokens=1000
        )

        # Telemetry: record feedback generation call
        try:
            log_api_call("chat", model="gpt-3.5-turbo", prompt_text=prompt, response=response, extra={"note": "trimmed_last_n"})
        except Exception:
            pass

        raw = response.choices[0].message.content
        try:
            logger.debug("LLM raw feedback: %s", raw)
        except Exception:
            pass

        data = parse_feedback_raw(raw, weights, qa_pairs, conversation)
        if data is None:
            logger.warning("Failed to parse LLM JSON response; saving raw for debugging.")
            fallback_raw = {
                "overall_score": 0,
                "verdict_title": "Interview Completed",
                "verdict_summary": "Feedback could not be parsed from LLM.",
                "skills": [],
                "strengths": [],
                "improvements": [],
                "final_verdict": "Feedback unavailable.",
                "detailed_feedback": "",
                "per_question_feedback": []
            }
            fallback_raw["raw_llm"] = raw
            return json.dumps(fallback_raw)

        return json.dumps(data)

    except Exception as e:
        # Log exception details for debugging
        logger.exception("generate_feedback failed: %s", e)
        fallback = {
            "overall_score": 0,
            "verdict_title": "Interview Completed",
            "verdict_summary": "Feedback could not be generated.",
            "skills": [{"name": k, "score": 0} for k in weights],
            "strengths": [],
            "improvements": ["Answer more questions for better accuracy."],
            "final_verdict": "Please try again later.",
            "detailed_feedback": "",
            "per_question_feedback": per_question_feedback,
            "ui_summary": "No score available."
        }

        return json.dumps(fallback)

# =========================
# Rephrase Question
# =========================
def rephrase_question(question):

    try:
        # Use a lower-cost model for short utility operations
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Rephrase clearly in one sentence."},
                {"role": "user", "content": question}
            ],
            temperature=0.25,
            max_tokens=48
        )
        try:
            log_api_call("chat", model="gpt-3.5-turbo", prompt_text=question, response=response)
        except Exception:
            pass
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
        # Use a cheaper model and limit tokens for short hints
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Give a short helpful hint."},
                {"role": "user", "content": f"Question: {question}\nRole: {role}\nStack: {', '.join(stack) if stack else 'General'}"}
            ],
            temperature=0.35,
            max_tokens=60
        )
        try:
            log_api_call("chat", model="gpt-3.5-turbo", prompt_text=question, response=response)
        except Exception:
            pass
        return response.choices[0].message.content.strip()
    except Exception:
        return "Focus on the core concept and explain your approach."
