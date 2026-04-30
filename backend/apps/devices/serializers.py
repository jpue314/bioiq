from rest_framework import serializers
from .models import ConnectedDevice


class ConnectedDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectedDevice
        fields = ["id", "provider", "last_synced_at", "is_active", "created_at"]
