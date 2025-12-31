from django.db import models

class Project(models.Model):

    PROJECT_TYPE_CHOICES = [
        ("personalized", "Personalized"),
        ("realtime", "Realtime / Startup"),
    ]

    TRACK_CHOICES = [
        ("10th", "10th"),
        ("intermediate", "Intermediate"),
        ("btech-cse", "BTech CSE"),
        ("btech-ece", "BTech ECE"),
        ("btech-ee", "BTech EE"),
        ("btech-me", "BTech ME"),
        ("btech-ai", "BTech AIML"),
    ]

    title = models.CharField(max_length=250)
    description = models.TextField()

    project_type = models.CharField(
        max_length=20,
        choices=PROJECT_TYPE_CHOICES
    )

    track = models.CharField(
        max_length=25,
        choices=TRACK_CHOICES
    )

    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.track})"
