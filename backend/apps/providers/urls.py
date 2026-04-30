from django.urls import path
from . import views

urlpatterns = [
    path("provider-access/", views.ProviderAccessListView.as_view(), name="provider-access-list"),
    path("provider-access/<int:pk>/", views.ProviderAccessDetailView.as_view(), name="provider-access-detail"),
]
