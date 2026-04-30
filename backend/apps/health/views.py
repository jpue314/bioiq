from django.utils import timezone
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.mixins import AuditMixin
from .models import DailyScore, HealthMetric
from .serializers import DailyScoreSerializer, HealthMetricSerializer


class TodayScoreView(AuditMixin, APIView):
    audit_resource_type = "DailyScore"

    def get(self, request: Request) -> Response:
        score = DailyScore.objects.filter(user=request.user, date=timezone.now().date()).first()
        if not score:
            return Response({"detail": "No score for today."}, status=status.HTTP_404_NOT_FOUND)
        self.log_read(request, str(score.pk))
        return Response(DailyScoreSerializer(score).data)


class ScoreHistoryView(AuditMixin, APIView):
    audit_resource_type = "DailyScore"

    def get(self, request: Request) -> Response:
        qs = DailyScore.objects.filter(user=request.user)
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)
        return Response(DailyScoreSerializer(qs, many=True).data)


class MetricsView(AuditMixin, APIView):
    audit_resource_type = "HealthMetric"

    def get(self, request: Request) -> Response:
        qs = HealthMetric.objects.filter(user=request.user)
        metric_type = request.query_params.get("type")
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        if metric_type:
            qs = qs.filter(metric_type=metric_type)
        if start:
            qs = qs.filter(recorded_at__date__gte=start)
        if end:
            qs = qs.filter(recorded_at__date__lte=end)
        return Response(HealthMetricSerializer(qs[:500], many=True).data)
