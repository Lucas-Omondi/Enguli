from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Alert
from .serializers import AlertSerializer
from accounts.permissions import IsAdminOrFieldEngineer


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related('station', 'sensor').all().order_by('-created_at')
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrFieldEngineer]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by resolved status
        resolved = self.request.query_params.get('resolved')
        if resolved is not None:
            if resolved in ['1', 'true', 'True']:
                queryset = queryset.filter(is_resolved=True)
            elif resolved in ['0', 'false', 'False']:
                queryset = queryset.filter(is_resolved=False)

        # Filter by station
        station_id = self.request.query_params.get('station_id')
        if station_id:
            queryset = queryset.filter(station_id=station_id)

        # Filter by severity (e.g. ?severity=critical)
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity__iexact=severity)

        return queryset

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Action to resolve an alert and record the resolution timestamp.
        """
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save()
        return Response({
            'status': 'Alert resolved successfully',
            'alert_id': alert.id,
            'resolved_at': alert.resolved_at
        }, status=status.HTTP_200_OK)