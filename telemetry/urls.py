from django.urls import path, include
from .views import TelemetryIngestView, SensorReadingViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'logs', SensorReadingViewSet, basename='telemetry-logs')

urlpatterns = [
    path('ingest/', TelemetryIngestView.as_view(), name='telemetry-ingest'),
    path('', include(router.urls)),
]