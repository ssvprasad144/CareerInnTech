# careerinntech/AI/interview_utils.py

INTRO_QUESTIONS = [
    "Tell me about yourself",
    "What are your strengths?",
    "What are your weaknesses?",
]


def generate_tts(*args, **kwargs):
    """Flexible TTS helper.

    Accepts either `generate_tts(text)` or `generate_tts(session_id, text)`
    and returns a short placeholder string (replace with real TTS
    generation when available).
    """
    # Determine text argument
    text = None
    if args:
        # If two args, assume (session_id, text)
        if len(args) >= 2:
            text = args[1]
        else:
            text = args[0]
    else:
        text = kwargs.get("text")

    if text is None:
        return ""

    return (str(text)[:200] + "...") if len(str(text)) > 200 else str(text)
