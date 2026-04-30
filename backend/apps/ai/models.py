from django.conf import settings
from django.db import models


class AIConversation(models.Model):
    class ConversationType(models.TextChoices):
        CHAT = "chat", "General Chat"
        INSIGHTS = "insights", "Health Insights"
        QUESTIONS = "questions", "Appointment Questions"
        WORKOUT = "workout", "Workout Plan"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_conversations")
    messages = models.JSONField(default=list)
    conversation_type = models.CharField(max_length=20, choices=ConversationType.choices, default=ConversationType.CHAT)
    model_used = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_conversations"
        ordering = ["-updated_at"]
