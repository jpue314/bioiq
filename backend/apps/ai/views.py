from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from .services import AIService
from .models import AIConversation
from .serializers import MessageSerializer, AIConversationSerializer


def _save_conversation(user, messages: list, reply: str, conv_type: str, model: str) -> None:
    all_messages = messages + [{"role": "assistant", "content": reply}]
    AIConversation.objects.create(
        user=user,
        messages=all_messages,
        conversation_type=conv_type,
        model_used=model,
    )


class ChatView(APIView):
    def post(self, request: Request) -> Response:
        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        messages = serializer.validated_data["messages"]
        service = AIService()
        reply = service.chat(user=request.user, messages=messages)
        _save_conversation(request.user, messages, reply, AIConversation.ConversationType.CHAT, "claude-haiku-4-5-20251001")
        return Response({"reply": reply})


class InsightsView(APIView):
    def post(self, request: Request) -> Response:
        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        messages = serializer.validated_data["messages"]
        service = AIService()
        reply = service.insights(user=request.user, messages=messages)
        _save_conversation(request.user, messages, reply, AIConversation.ConversationType.INSIGHTS, "claude-sonnet-4-6")
        return Response({"reply": reply})


class QuestionsView(APIView):
    def post(self, request: Request) -> Response:
        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        messages = serializer.validated_data["messages"]
        service = AIService()
        reply = service.compile_questions(user=request.user, messages=messages)
        _save_conversation(request.user, messages, reply, AIConversation.ConversationType.QUESTIONS, "claude-haiku-4-5-20251001")
        return Response({"reply": reply})


class WorkoutPlanView(APIView):
    def post(self, request: Request) -> Response:
        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        messages = serializer.validated_data["messages"]
        service = AIService()
        reply = service.workout_plan(user=request.user, messages=messages)
        _save_conversation(request.user, messages, reply, AIConversation.ConversationType.WORKOUT, "claude-sonnet-4-6")
        return Response({"reply": reply})


class ConversationHistoryView(APIView):
    def get(self, request: Request) -> Response:
        conversations = AIConversation.objects.filter(user=request.user)[:20]
        return Response(AIConversationSerializer(conversations, many=True).data)
