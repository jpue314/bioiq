import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_register_creates_user_and_returns_tokens(api_client):
    url = reverse("auth-register")
    response = api_client.post(url, {
        "email": "new@example.com",
        "password": "StrongPass123!",
        "first_name": "Jane",
        "last_name": "Doe",
    }, format="json")
    assert response.status_code == 201
    assert "access" in response.data
    assert response.cookies.get("refresh_token") is not None


@pytest.mark.django_db
def test_login_returns_access_token_and_sets_cookie(api_client, user):
    url = reverse("auth-login")
    response = api_client.post(url, {
        "email": user.email,
        "password": "TestPassword123!",
    }, format="json")
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" not in response.data
    assert response.cookies.get("refresh_token") is not None


@pytest.mark.django_db
def test_logout_clears_refresh_cookie(auth_client):
    url = reverse("auth-logout")
    response = auth_client.post(url)
    assert response.status_code == 200
    assert response.cookies["refresh_token"].value == ""


@pytest.mark.django_db
def test_unauthenticated_request_returns_401(api_client):
    url = reverse("user-me")
    response = api_client.get(url)
    assert response.status_code == 401
