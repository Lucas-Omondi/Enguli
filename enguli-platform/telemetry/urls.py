from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TelemetryIngestView, SensorReadingViewSet, ExportTelemetryCSVView

router = DefaultRouter()
router.register(r'logs', SensorReadingViewSet, basename='telemetry-logs')

urlpatterns = [
    path('ingest/', TelemetryIngestView.as_view(), name='telemetry-ingest'),
    path('export/csv/', ExportTelemetryCSVView.as_view(), name='export-telemetry-csv'),
    path('', include(router.urls)),
]