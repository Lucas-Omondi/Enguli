from rest_framework import viewsets
from .models import Alert
from .serializers import AlertSerializer


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related('station', 'sensor').all().order_by('-created_at')
    serializer_class = AlertSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by resolved status
        resolved = self.request.query_params.get('resolved')

        if resolved is not None:
            if resolved in ['1', 'true', 'True']:
                queryset = queryset.filter(is_resolved=True)
            elif resolved in ['0', 'false', 'False']:
                queryset = queryset.filter(is_resolved=False)

        # Optional filter by station
        station_id = self.request.query_params.get('station_id')
        if station_id:
            queryset = queryset.filter(station_id=station_id)

        return queryset