import pytest
from apps.audit.models import AuditLog


@pytest.mark.django_db
def test_audit_log_records_phi_access(user):
    log = AuditLog.objects.create(
        user=user,
        actor=user,
        action=AuditLog.Action.READ,
        resource_type="HealthProfile",
        resource_id=str(user.pk),
        ip_address="127.0.0.1",
        user_agent="pytest",
    )
    assert log.pk is not None
    assert log.action == AuditLog.Action.READ
    assert log.user == user


@pytest.mark.django_db
def test_audit_log_str(user):
    log = AuditLog.objects.create(
        user=user,
        actor=user,
        action=AuditLog.Action.WRITE,
        resource_type="DailyScore",
        resource_id="1",
        ip_address="127.0.0.1",
        user_agent="test",
    )
    assert "DailyScore" in str(log)
