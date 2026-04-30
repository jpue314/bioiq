from .models import AuditLog


class AuditMixin:
    audit_resource_type: str = ""

    def _log(self, request, action: str, resource_id: str) -> None:
        if not request.user.is_authenticated:
            return
        AuditLog.objects.create(
            user=request.user,
            actor=request.user,
            action=action,
            resource_type=self.audit_resource_type,
            resource_id=resource_id,
            ip_address=request.META.get("REMOTE_ADDR", "0.0.0.0"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

    def log_read(self, request, resource_id: str) -> None:
        self._log(request, AuditLog.Action.READ, resource_id)

    def log_write(self, request, resource_id: str) -> None:
        self._log(request, AuditLog.Action.WRITE, resource_id)

    def log_delete(self, request, resource_id: str) -> None:
        self._log(request, AuditLog.Action.DELETE, resource_id)
