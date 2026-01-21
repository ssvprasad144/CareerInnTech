from django.urls import path
from . import views, voice_views
from .voice_views import voice_next_question, voice_hint, voice_skip_question

urlpatterns = [
    path('interview-preparation/', views.interview_preparation, name='interview-preparation'),
    path('interview-preparation/types/', views.interview_types, name='interview-types'),
    path('interview-preparation/tips/', views.interview_tips, name='interview-tips'),
    path('interview-preparation/myths/', views.interview_myths, name='interview-myths'),
    path('interview-preparation/question-bank/', views.interview_question_bank, name='interview-question-bank'),
    path('interview-preparation/resume-prep/', views.interview_resume_prep, name='interview-resume-prep'),
    path('interview-preparation/communication/', views.interview_communication, name='interview-communication'),

    # Landing & setup
    path('', views.ai_mock_interview_landing, name='ai_index'),
    path('ai-mock-interview/', views.ai_mock_interview_landing, name='ai-mock-interview'),
    path('ai-interview-select/', views.ai_interview_select, name='ai-interview-select'),
    path('ai-interview-config/<str:interview_type>/', views.interview_config, name='ai-interview-config'),

    # Start → Live
    path('ai-interview-start/', views.start_interview, name='ai-interview-start'),
    path('ai-interview-live/', views.ai_interview_live, name='ai-interview-live'),

    # Voice pipeline
    path('voice/next/', voice_next_question, name='ai-voice-next'),
    path('voice/hint/', voice_hint, name='ai-voice-hint'),
    path('voice/skip/', voice_skip_question, name='ai-voice-skip'),
    path('stt/', views.stt_transcribe, name='ai-stt'),

    # Finish
    path('finish/', views.finish_interview, name='finish_interview'),
    path('feedback/<int:session_id>/', views.interview_feedback_page, name='interview-feedback'),
    path('feedback/<int:session_id>/details/', views.interview_feedback_details, name='interview-feedback-details'),
    path('feedback/<int:session_id>/download/', views.download_feedback_pdf, name='interview-feedback-download'),
        path('submit_code/', voice_views.submit_code, name='ai_submit_code'),
]
