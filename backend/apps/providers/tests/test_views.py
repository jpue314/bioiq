import pytest
from django.urls import reverse
from apps.providers.models import ProviderAccess


@pytest.mark.django_db
def test_grant_provider_access(auth_client, user):
    response = auth_client.post(reverse("provider-access-list"), {
        "provider_name": "Dr. Smith",
        "provider_email": "drsmith@clinic.com",
        "provider_type": "physician",
        "access_level": "read_summary",
    }, format="json")
    assert response.status_code == 201
    assert ProviderAccess.objects.filter(patient=user).count() == 1


@pytest.mark.django_db
def test_revoke_provider_access(auth_client, user):
    access = ProviderAccess.objects.create(
        patient=user,
        provider_name="Dr. Jones",
        provider_email="drjones@clinic.com",
    )
    response = auth_client.delete(reverse("provider-access-detail", args=[access.pk]))
    assert response.status_code == 204
    access.refresh_from_db()
    assert access.revoked_at is not None
