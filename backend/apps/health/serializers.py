from rest_framework import serializers
from .models import DailyScore, HealthMetric


class DailyScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyScore
        fields = ["id", "date", "readiness_score", "sleep_score", "recovery_score", "activity_score", "score_breakdown"]


class HealthMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthMetric
        fields = ["id", "metric_type", "value", "unit", "recorded_at"]
