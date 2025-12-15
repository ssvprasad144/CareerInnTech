from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    track = models.CharField(max_length=50)
    education = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    year = models.CharField(max_length=50)
    college = models.CharField(max_length=200)
    career_goal = models.CharField(max_length=200)

    about = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
