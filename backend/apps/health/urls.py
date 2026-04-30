from django.urls import path
from . import views

urlpatterns = [
    path("scores/today/", views.TodayScoreView.as_view(), name="scores-today"),
    path("scores/", views.ScoreHistoryView.as_view(), name="scores-history"),
    path("metrics/", views.MetricsView.as_view(), name="health-metrics"),
]
