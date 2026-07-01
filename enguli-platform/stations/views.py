from rest_framework import viewsets
from .models import Station
from .serializers import StationSerializer
from rest_framework import viewsets
from .models import Sensor
from .serializers import SensorSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all().order_by('-created_at')
    serializer_class = StationSerializer

class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.select_related('station').all().order_by('-created_at')
    serializer_class = SensorSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        station_id = self.request.query_params.get('station_id')
        if station_id:
            queryset = queryset.filter(station_id=station_id)

        return queryset