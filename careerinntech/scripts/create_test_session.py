import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'careerinntech.settings')
import django
django.setup()

from AI.models import InterviewSession

s = InterviewSession.objects.create(user=None, interview_type='web')
print(s.id)
