import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'careerinntech.settings')
django.setup()
from AI.models import InterviewSession
s = InterviewSession.objects.create(user=None, interview_type='software')
print(s.id)
