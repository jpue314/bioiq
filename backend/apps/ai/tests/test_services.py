import pytest
from unittest.mock import patch, MagicMock
from apps.ai.services import AIService, ModelRoute


def test_chat_routes_to_haiku():
    service = AIService.__new__(AIService)
    assert service._model_for(ModelRoute.CHAT) == "claude-haiku-4-5-20251001"


def test_insights_routes_to_sonnet():
    service = AIService.__new__(AIService)
    assert service._model_for(ModelRoute.INSIGHTS) == "claude-sonnet-4-6"


@pytest.mark.django_db
def test_ai_service_sends_user_context(user):
    with patch("apps.ai.services.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="Here are your insights.")],
            model="claude-haiku-4-5-20251001",
        )
        service = AIService(api_key="test-key")
        result = service.chat(user=user, messages=[{"role": "user", "content": "How am I doing?"}])
        assert "Here are your insights." in result
        call_kwargs = mock_client.messages.create.call_args[1]
        assert "BioIQ" in call_kwargs["system"]
