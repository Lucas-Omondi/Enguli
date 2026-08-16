from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Station, Sensor
from .serializers import StationSerializer, SensorSerializer, UserDetailSerializer
from rest_framework import viewsets
from .permissions import IsAdminOrFieldEngineer
from .serializers import SensorSerializer

class CurrentUserView(APIView):
    """
    Returns authenticated user information and their assigned role.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all().order_by('-created_at')
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