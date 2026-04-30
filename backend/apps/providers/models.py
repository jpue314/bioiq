from django.conf import settings
from django.db import models


class ProviderAccess(models.Model):
    class AccessLevel(models.TextChoices):
        SUMMARY = "read_summary", "Read Summary"
        FULL = "read_full", "Read Full"
        METRICS = "read_metrics", "Read Metrics"

    class ProviderType(models.TextChoices):
        PHYSICIAN = "physician", "Physician"
        COACH = "coach", "Health Coach"
        SPECIALIST = "specialist", "Specialist"
        OTHER = "other", "Other"

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="provider_accesses")
    provider_name = models.CharField(max_length=200)
    provider_email = models.EmailField()
    provider_type = models.CharField(max_length=20, choices=ProviderType.choices, default=ProviderType.OTHER)
    access_level = models.CharField(max_length=20, choices=AccessLevel.choices, default=AccessLevel.SUMMARY)
    authorized_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "provider_accesses"

    @property
    def is_active(self) -> bool:
        from django.utils import timezone
        if self.revoked_at:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True
