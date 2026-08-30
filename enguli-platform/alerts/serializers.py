from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    station_code = serializers.CharField(source='station.station_code', read_only=True)
    station_name = serializers.CharField(source='station.station_name', read_only=True)
    sensor_serial = serializers.CharField(source='sensor.serial_number', read_only=True, default=None)
    sensor_code = serializers.CharField(source='sensor.sensor_code', read_only=True, default=None)

    class Meta:
        model = Alert
        fields = [
            'id',
            'station',
            'station_code',
            'station_name',
            'sensor',
            'sensor_serial',
            'sensor_code',
            'severity',
            'alert_type',
            'message',
            'is_resolved',
            'created_at',
            'resolved_at'
        ]