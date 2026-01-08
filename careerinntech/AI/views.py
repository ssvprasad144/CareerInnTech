from django.shortcuts import render

def interview_preparation(request):
    """
    Interview Preparation main hub page
    """
    return render(request, 'ai/interview_preparation.html')

from django.shortcuts import render

def ai_mock_interview_landing(request):
    return render(request, 'ai/ai_mock_interview.html')

def ai_interview_session(request):
    return render(request, 'ai/ai_interview_session.html')
def ai_interview_select(request):
    return render(request, 'ai/ai_interview_select.html')
