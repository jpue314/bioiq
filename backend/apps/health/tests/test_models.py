import pytest
from apps.health.models import DailyScore, HealthMetric


@pytest.mark.django_db
def test_daily_score_created_for_user(user):
    score = DailyScore.objects.create(
        user=user,
        date="2026-04-29",
        readiness_score=82,
        sleep_score=78,
        recovery_score=85,
        activity_score=80,
        score_breakdown={"hrv": 65, "resting_hr": 52},
    )
    assert score.readiness_score == 82
    assert score.score_breakdown["hrv"] == 65


@pytest.mark.django_db
def test_health_metric_stores_raw_value(user):
    metric = HealthMetric.objects.create(
        user=user,
        source=None,
        metric_type=HealthMetric.MetricType.HRV,
        value=65.0,
        unit="ms",
        recorded_at="2026-04-29T06:00:00Z",
    )
    assert metric.metric_type == HealthMetric.MetricType.HRV
    assert metric.value == 65.0
