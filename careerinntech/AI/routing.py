from django.urls import re_path
from .consumers import InterviewVoiceConsumer

websocket_urlpatterns = [
    re_path(r"ws/interview/(?P<session_id>\d+)/$", InterviewVoiceConsumer.as_asgi()),
]
