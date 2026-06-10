from rest_framework import serializers
from .models import Station, Sensor


class StationSerializer(serializers.ModelSerializer):

    sensor_count = serializers.SerializerMethodField()

    class Meta:
        model = Station
        fields = [
            'id',
            'station_code',
            'station_name',
            'latitude',
            'longitude',
            'location_description',
            'status',
            'created_at',
            'sensor_count'
        ]

    def get_sensor_count(self, obj):
        return obj.sensors.count()

class SensorSerializer(serializers.ModelSerializer):

    station_code = serializers.CharField(
        source='station.station_code',
        read_only=True
    )

    class Meta:
        model = Sensor
        fields = [
            'id',
            'station',
            'station_code',
            'sensor_type',
            'serial_number',
            'battery_level',
            'connectivity_status',
            'calibration_offset',
            'is_active',
            'created_at'
        ]