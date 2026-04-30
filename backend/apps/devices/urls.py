from django.urls import path
from . import views

urlpatterns = [
    path("devices/", views.DeviceListView.as_view(), name="devices-list"),
    path("devices/<int:pk>/", views.DeviceDetailView.as_view(), name="devices-detail"),
]
