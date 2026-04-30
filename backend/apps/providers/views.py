from django.utils import timezone
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.audit.mixins import AuditMixin
from .models import ProviderAccess
from .serializers import ProviderAccessSerializer


class ProviderAccessListView(AuditMixin, APIView):
    audit_resource_type = "ProviderAccess"

    def get(self, request: Request) -> Response:
        accesses = ProviderAccess.objects.filter(patient=request.user)
        return Response(ProviderAccessSerializer(accesses, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = ProviderAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access = serializer.save(patient=request.user)
        self.log_write(request, str(access.pk))
        return Response(ProviderAccessSerializer(access).data, status=status.HTTP_201_CREATED)


class ProviderAccessDetailView(AuditMixin, APIView):
    audit_resource_type = "ProviderAccess"

    def delete(self, request: Request, pk: int) -> Response:
        access = ProviderAccess.objects.filter(pk=pk, patient=request.user).first()
        if not access:
            return Response(status=status.HTTP_404_NOT_FOUND)
        access.revoked_at = timezone.now()
        access.save(update_fields=["revoked_at"])
        self.log_delete(request, str(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)
