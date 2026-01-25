from django.db import models
from django.contrib.auth.models import User 

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    track = models.CharField(max_length=50, blank=True)
    education = models.CharField(max_length=100, blank=True)
    branch = models.CharField(max_length=100, blank=True)
    year = models.CharField(max_length=50, blank=True)
    college = models.CharField(max_length=200, blank=True)
    university = models.CharField(max_length=150, blank=True)
    career_goal = models.CharField(max_length=200, blank=True)
    about = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    is_profile_complete = models.BooleanField(default=False)

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


class Opportunity(models.Model):
    TYPE_CHOICES = [
        ("job", "Job"),
        ("internship", "Internship"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("upcoming", "Upcoming"),
        ("closed", "Closed"),
    ]

    title = models.CharField(max_length=200)

    opportunity_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="job"
    )

    companies = models.CharField(
        max_length=300,
        help_text="Example: Amazon • Google • Startups"
    )

    eligibility = models.CharField(max_length=200)

    package = models.CharField(
        max_length=100,
        help_text="Example: ₹6–30 LPA or ₹15k/month"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide from students"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.opportunity_type})"


class Project(models.Model):
    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    title = models.CharField(max_length=200)

    description = models.TextField(
        help_text="Short description of the project"
    )

    tech_stack = models.CharField(
        max_length=200,
        help_text="Example: Python, Django, PostgreSQL"
    )

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default="beginner"
    )

    github_link = models.URLField(
        blank=True,
        null=True,
        help_text="Optional GitHub repository link"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide from students"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

class UserContextMemory(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    career_goal = models.CharField(max_length=200, blank=True)
    branch = models.CharField(max_length=100, blank=True)
    education_level = models.CharField(max_length=100, blank=True)

    target_roles = models.CharField(max_length=200, blank=True)
    skills = models.TextField(blank=True)
    weak_areas = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class SignupOTP(models.Model):
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created:
        StudentProfile.objects.create(user=instance)


