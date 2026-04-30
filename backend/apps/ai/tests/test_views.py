import pytest
from django.urls import reverse
from unittest.mock import patch


@pytest.mark.django_db
def test_chat_endpoint_returns_ai_response(auth_client):
    with patch("apps.ai.views.AIService") as mock_service_class:
        mock_service_class.return_value.chat.return_value = "Here is my response."
        response = auth_client.post(reverse("ai-chat"), {
            "messages": [{"role": "user", "content": "How is my sleep?"}]
        }, format="json")
    assert response.status_code == 200
    assert response.data["reply"] == "Here is my response."


@pytest.mark.django_db
def test_insights_endpoint_requires_auth(api_client):
    response = api_client.post(reverse("ai-insights"), {}, format="json")
    assert response.status_code == 401
