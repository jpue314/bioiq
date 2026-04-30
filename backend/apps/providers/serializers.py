from rest_framework import serializers
from .models import ProviderAccess


class ProviderAccessSerializer(serializers.ModelSerializer):
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = ProviderAccess
        fields = ["id", "provider_name", "provider_email", "provider_type",
                  "access_level", "authorized_at", "expires_at", "is_active"]
        read_only_fields = ["id", "authorized_at", "is_active"]
