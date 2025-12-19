from django.db import models

class BranchVideo(models.Model):
    BRANCH_CHOICES = [
        ("cse", "Computer Science"),
        ("ece", "Electronics & Communication"),
        ("eee", "Electrical Engineering"),
        ("mech", "Mechanical Engineering"),
        ("civil", "Civil Engineering"),
    ]

    branch = models.CharField(
        max_length=20,
        choices=BRANCH_CHOICES,
        unique=True
    )

    video_url = models.URLField(
        blank=True,
        help_text="Use YouTube embed URL"
    )

    is_active = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_branch_display()
