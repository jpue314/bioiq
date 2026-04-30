import pytest
from django.urls import reverse
from apps.devices.models import ConnectedDevice


@pytest.mark.django_db
def test_list_devices_returns_user_devices(auth_client, user):
    ConnectedDevice.objects.create(
        user=user, provider="whoop", access_token="tok", refresh_token="ref"
    )
    response = auth_client.get(reverse("devices-list"))
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["provider"] == "whoop"


@pytest.mark.django_db
def test_delete_device_removes_it(auth_client, user):
    device = ConnectedDevice.objects.create(
        user=user, provider="garmin", access_token="tok", refresh_token="ref"
    )
    response = auth_client.delete(reverse("devices-detail", args=[device.pk]))
    assert response.status_code == 204
    assert not ConnectedDevice.objects.filter(pk=device.pk).exists()


@pytest.mark.django_db
def test_cannot_delete_another_users_device(auth_client, db):
    from apps.users.tests.factories import UserFactory
    other_user = UserFactory()
    device = ConnectedDevice.objects.create(
        user=other_user, provider="fitbit", access_token="tok", refresh_token="ref"
    )
    response = auth_client.delete(reverse("devices-detail", args=[device.pk]))
    assert response.status_code == 404
