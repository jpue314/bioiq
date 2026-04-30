from django.conf import settings
from django.db import models


class DailyScore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="daily_scores")
    date = models.DateField()
    readiness_score = models.PositiveSmallIntegerField()
    sleep_score = models.PositiveSmallIntegerField(null=True, blank=True)
    recovery_score = models.PositiveSmallIntegerField(null=True, blank=True)
    activity_score = models.PositiveSmallIntegerField(null=True, blank=True)
    score_breakdown = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "daily_scores"
        unique_together = [("user", "date")]
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.user.email} - {self.date} - {self.readiness_score}"


class HealthMetric(models.Model):
    class MetricType(models.TextChoices):
        HRV = "hrv", "HRV"
        RESTING_HR = "resting_hr", "Resting Heart Rate"
        STEPS = "steps", "Steps"
        SLEEP_DURATION = "sleep_duration", "Sleep Duration"
        SLEEP_QUALITY = "sleep_quality", "Sleep Quality"
        CALORIES = "calories", "Calories Burned"
        OXYGEN_SAT = "spo2", "Blood Oxygen Saturation"
        STRESS = "stress", "Stress Score"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="health_metrics")
    source = models.ForeignKey("devices.ConnectedDevice", on_delete=models.SET_NULL, null=True, blank=True)
    metric_type = models.CharField(max_length=30, choices=MetricType.choices)
    value = models.FloatField()
    unit = models.CharField(max_length=20)
    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "health_metrics"
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["user", "metric_type", "recorded_at"]),
        ]
