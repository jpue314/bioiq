from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ConnectedDevice
from .serializers import ConnectedDeviceSerializer


class DeviceListView(APIView):
    def get(self, request: Request) -> Response:
        devices = ConnectedDevice.objects.filter(user=request.user, is_active=True)
        return Response(ConnectedDeviceSerializer(devices, many=True).data)


class DeviceDetailView(APIView):
    def delete(self, request: Request, pk: int) -> Response:
        device = ConnectedDevice.objects.filter(pk=pk, user=request.user).first()
        if not device:
            return Response(status=status.HTTP_404_NOT_FOUND)
        device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
