import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_user_created_with_email_as_identifier():
    user = User.objects.create_user(
        email="test@example.com",
        password="SecurePass123!",
        first_name="Jane",
        last_name="Doe",
    )
    assert user.email == "test@example.com"
    assert user.USERNAME_FIELD == "email"
    assert user.check_password("SecurePass123!")
    assert not user.is_verified


@pytest.mark.django_db
def test_user_email_must_be_unique():
    User.objects.create_user(email="dup@example.com", password="Pass123456!")
    with pytest.raises(Exception):
        User.objects.create_user(email="dup@example.com", password="Pass123456!")


@pytest.mark.django_db
def test_health_profile_created_for_user():
    from apps.users.models import HealthProfile
    user = User.objects.create_user(email="hp@example.com", password="Pass123456!")
    profile = HealthProfile.objects.create(
        user=user,
        date_of_birth="1990-01-01",
        biological_sex="M",
        height_cm=180,
        weight_kg=80.0,
    )
    assert profile.user == user
    assert profile.height_cm == 180
