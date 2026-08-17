from rest_framework import viewsets
from .models import Station, Sensor
from .serializers import StationSerializer, SensorSerializer
from accounts.permissions import IsAdminOrFieldEngineer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all().order_by('station_code')
    serializer_class = StationSerializer
    permission_classes = [IsAdminOrFieldEngineer]


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.select_related('station').all().order_by('-created_at')
    serializer_class = SensorSerializer
    permission_classes = [IsAdminOrFieldEngineer]

    def get_queryset(self):
        queryset = super().get_queryset()
        station_id = self.request.query_params.get('station_id')
        if station_id:
            queryset = queryset.filter(station_id=station_id)
        return queryset