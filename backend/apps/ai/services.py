from enum import Enum
from typing import Any
import anthropic
from django.conf import settings


class ModelRoute(str, Enum):
    CHAT = "chat"
    INSIGHTS = "insights"
    QUESTIONS = "questions"
    WORKOUT = "workout"


MODEL_MAP = {
    ModelRoute.CHAT: "claude-haiku-4-5-20251001",
    ModelRoute.QUESTIONS: "claude-haiku-4-5-20251001",
    ModelRoute.INSIGHTS: "claude-sonnet-4-6",
    ModelRoute.WORKOUT: "claude-sonnet-4-6",
}

SYSTEM_PROMPT = """You are BioIQ AI, a personal health intelligence assistant.
You have access to the user health data provided below. Use it to give personalized,
evidence-based guidance. Be clear, supportive, and appropriately cautious -- always
recommend consulting a healthcare professional for medical decisions.

Never fabricate health data. If you are uncertain, say so."""


class AIService:
    def __init__(self, api_key: str | None = None) -> None:
        self.client = anthropic.Anthropic(api_key=api_key or settings.ANTHROPIC_API_KEY)

    def _model_for(self, route: ModelRoute) -> str:
        return MODEL_MAP[route]

    def _build_system_prompt(self, user) -> str:
        from apps.health.models import DailyScore

        context_lines = [SYSTEM_PROMPT, f"\nUser: {user.first_name} {user.last_name}"]
        try:
            profile = user.health_profile
            if profile.date_of_birth:
                context_lines.append(f"Date of birth: {profile.date_of_birth}")
            if profile.fitness_goals:
                context_lines.append(f"Fitness goals: {', '.join(profile.fitness_goals)}")
        except Exception:
            pass

        recent_scores = DailyScore.objects.filter(user=user).order_by("-date")[:7]
        if recent_scores:
            context_lines.append("\nRecent readiness scores (last 7 days):")
            for score in recent_scores:
                context_lines.append(f"  {score.date}: {score.readiness_score}/100")

        return "\n".join(context_lines)

    def _call(self, route: ModelRoute, user, messages: list[dict[str, Any]]) -> str:
        safe_messages = [
            {"role": m["role"], "content": str(m["content"])[:4000]}
            for m in messages
        ]
        response = self.client.messages.create(
            model=self._model_for(route),
            max_tokens=1024,
            system=self._build_system_prompt(user),
            messages=safe_messages,
        )
        return response.content[0].text

    def chat(self, user, messages: list[dict[str, Any]]) -> str:
        return self._call(ModelRoute.CHAT, user, messages)

    def insights(self, user, messages: list[dict[str, Any]]) -> str:
        return self._call(ModelRoute.INSIGHTS, user, messages)

    def compile_questions(self, user, messages: list[dict[str, Any]]) -> str:
        return self._call(ModelRoute.QUESTIONS, user, messages)

    def workout_plan(self, user, messages: list[dict[str, Any]]) -> str:
        return self._call(ModelRoute.WORKOUT, user, messages)
