from django.conf import settings
from django.db import models


class ConnectedDevice(models.Model):
    class Provider(models.TextChoices):
        WHOOP = "whoop", "Whoop"
        APPLE_HEALTH = "apple_health", "Apple Health"
        GARMIN = "garmin", "Garmin"
        FITBIT = "fitbit", "Fitbit"
        STRAVA = "strava", "Strava"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="devices")
    provider = models.CharField(max_length=20, choices=Provider.choices)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "connected_devices"
        unique_together = [("user", "provider")]
