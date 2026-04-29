from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/", include("apps.health.urls")),
    path("api/", include("apps.devices.urls")),
    path("api/", include("apps.providers.urls")),
    path("api/ai/", include("apps.ai.urls")),
]
