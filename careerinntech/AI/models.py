from django.db import models
from django.conf import settings


class InterviewSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    interview_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.id} - {self.interview_type}"


class InterviewMessage(models.Model):
    session = models.ForeignKey(
        InterviewSession,
        related_name="messages",
        on_delete=models.CASCADE
    )
    sender = models.CharField(
        max_length=10,
        choices=(("user", "User"), ("ai", "AI"))
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.upper()} - {self.session.id}"
