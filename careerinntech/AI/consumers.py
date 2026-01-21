import json
from channels.generic.websocket import AsyncWebsocketConsumer
from openai import OpenAI
from django.conf import settings
from .interview_utils import generate_tts_bytes

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class InterviewVoiceConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        # audio chunk received
        if bytes_data:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=bytes_data
            )

            user_text = transcript.text

            # stream GPT response
            stream = client.responses.stream(
                model="gpt-4.1-mini",
                input=user_text
            )

            async for event in stream:
                if event.type == "response.output_text.delta":
                    await self.send(json.dumps({
                        "type": "text",
                        "delta": event.delta
                    }))

                if event.type == "response.completed":
                    # generate TTS
                    audio_bytes = generate_tts_bytes(event.output_text)
                    if audio_bytes:
                        await self.send(bytes_data=audio_bytes)
