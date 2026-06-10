from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):

    station_code = serializers.CharField(source='station.station_code', read_only=True)
    sensor_serial = serializers.CharField(source='sensor.serial_number', read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id',
            'station',
            'station_code',
            'sensor',
            'sensor_serial',
            'severity',
            'alert_type',
            'message',
            'is_resolved',
            'created_at'
        ]