import pytest
from django.urls import reverse
from django.utils import timezone
from apps.health.tests.factories import DailyScoreFactory


@pytest.mark.django_db
def test_today_score_returns_readiness(auth_client, user):
    DailyScoreFactory(user=user, date=timezone.now().date(), readiness_score=77)
    response = auth_client.get(reverse("scores-today"))
    assert response.status_code == 200
    assert response.data["readiness_score"] == 77


@pytest.mark.django_db
def test_today_score_returns_404_when_no_score_exists(auth_client):
    response = auth_client.get(reverse("scores-today"))
    assert response.status_code == 404


@pytest.mark.django_db
def test_score_history_returns_date_range(auth_client, user):
    DailyScoreFactory(user=user, date="2026-04-27", readiness_score=70)
    DailyScoreFactory(user=user, date="2026-04-28", readiness_score=80)
    DailyScoreFactory(user=user, date="2026-04-29", readiness_score=90)
    url = reverse("scores-history") + "?start=2026-04-27&end=2026-04-28"
    response = auth_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 2


@pytest.mark.django_db
def test_scores_are_scoped_to_authenticated_user(auth_client, user, db):
    from apps.users.tests.factories import UserFactory
    other_user = UserFactory()
    DailyScoreFactory(user=other_user, date=timezone.now().date(), readiness_score=99)
    response = auth_client.get(reverse("scores-today"))
    assert response.status_code == 404
