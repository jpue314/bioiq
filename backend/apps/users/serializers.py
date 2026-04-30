from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import HealthProfile

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=12, write_only=True)
    first_name = serializers.CharField(max_length=150, default="")
    last_name = serializers.CharField(max_length=150, default="")

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data: dict) -> dict:
        user = User.objects.create_user(**validated_data)
        HealthProfile.objects.create(user=user)
        refresh = RefreshToken.for_user(user)
        return {"user": user, "access": str(refresh.access_token), "refresh": str(refresh)}


class HealthProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProfile
        fields = ["date_of_birth", "biological_sex", "height_cm", "weight_kg", "fitness_goals", "medical_conditions"]


class UserSerializer(serializers.ModelSerializer):
    health_profile = HealthProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "is_verified", "created_at", "health_profile"]
        read_only_fields = ["id", "email", "is_verified", "created_at"]
