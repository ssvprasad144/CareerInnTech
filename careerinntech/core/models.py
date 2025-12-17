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

class College(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    annual_fee = models.IntegerField()  # in INR
    eamcet_rank_min = models.IntegerField()
    eamcet_rank_max = models.IntegerField()
    exam_type = models.CharField(max_length=50)  # TS EAMCET, AP EAMCET
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
