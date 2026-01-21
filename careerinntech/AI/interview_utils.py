from django.conf import settings
import os
import hashlib
from openai import OpenAI
import tempfile
import base64
from .telemetry import log_api_call

try:
    import azure.cognitiveservices.speech as speechsdk
    _AZURE_SPEECH_AVAILABLE = True
except Exception:
    speechsdk = None
    _AZURE_SPEECH_AVAILABLE = False

client = OpenAI(api_key=settings.OPENAI_API_KEY)

INTRO_QUESTIONS = [
    "Tell me about yourself.",
    "What role are you currently preparing for?",
    "How many years of experience do you have?",
    "Which technologies or skills are you most confident in?"
]


def _use_azure_tts():
    return (
        _AZURE_SPEECH_AVAILABLE
        and bool(getattr(settings, "AZURE_SPEECH_KEY", None))
        and bool(getattr(settings, "AZURE_SPEECH_REGION", None))
    )


def _azure_speech_config():
    speech_config = speechsdk.SpeechConfig(
        subscription=settings.AZURE_SPEECH_KEY,
        region=settings.AZURE_SPEECH_REGION
    )
    speech_config.speech_synthesis_voice_name = settings.AZURE_SPEECH_VOICE
    return speech_config


def generate_tts_bytes(text):
    try:
        if _use_azure_tts():
            speech_config = _azure_speech_config()
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=None
            )
            result = synthesizer.speak_text_async(text).get()
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            print("AZURE TTS ERROR:", result.reason)
            return None

        resp = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=settings.OPENAI_TTS_VOICE,
            input=text
        )
        try:
            log_api_call("tts", model="gpt-4o-mini-tts", prompt_text=text, response=resp)
        except Exception:
            pass
        return resp.read()

    except Exception as e:
        print("TTS BYTES ERROR:", e)
        return None


def generate_tts(session_id, text):
    try:
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()[:10]
        audio_filename = f"ai_question_session_{session_id}_{text_hash}.mp3"
        # Always use ephemeral flow: return data-URL audio, do not persist on disk.
        # This enforces 'never stores AI voices' policy.
        # Ephemeral flow: write to a temp file (for Azure path) or use in-memory bytes,
        # then return a data URL so frontend can play without server-side persistence.
        if _use_azure_tts():
            speech_config = _azure_speech_config()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp_path = tmp.name
            try:
                audio_config = speechsdk.audio.AudioOutputConfig(filename=tmp_path)
                synthesizer = speechsdk.SpeechSynthesizer(
                    speech_config=speech_config,
                    audio_config=audio_config
                )
                result = synthesizer.speak_text_async(text).get()
                if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
                    print("AZURE TTS ERROR:", result.reason)
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
                    return None
                with open(tmp_path, "rb") as f:
                    audio_bytes = f.read()
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
        else:
            audio_bytes = generate_tts_bytes(text)
            if not audio_bytes:
                return None

        b64 = base64.b64encode(audio_bytes).decode("ascii")
        data_url = f"data:audio/mpeg;base64,{b64}"
        return data_url

    except Exception as e:
        print("TTS ERROR:", e)
        return None
