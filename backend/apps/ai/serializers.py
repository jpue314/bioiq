from rest_framework import serializers
from .models import AIConversation


class MessageSerializer(serializers.Serializer):
    messages = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=50,
    )


class AIConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIConversation
        fields = ["id", "messages", "conversation_type", "model_used", "created_at", "updated_at"]
