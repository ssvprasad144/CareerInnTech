from django.urls import path
from . import views

urlpatterns = [
    path('interview-preparation/', views.interview_preparation, name='interview-preparation'),
    path('ai-mock-interview/', views.ai_mock_interview_landing, name='ai-mock-interview'),
    path('ai-interview-select/', views.ai_interview_select, name='ai-interview-select'),
    path('ai-interview-session/', views.ai_interview_session, name='ai-interview-session'),
]

