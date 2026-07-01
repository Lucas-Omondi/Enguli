from rest_framework import serializers
from.models import SensorReading


class SensorIngestSerializer(serializers.Serializer):
    sensor_serial = serializers.CharField()
    water_level = serializers.FloatField()
    battery_level = serializers.FloatField(required=False)
    signal_strength = serializers.FloatField(required=False)

class SensorReadingSerializer(serializers.ModelSerializer):
    station_code = serializers.CharField(source='station.station_code', read_only=True)
    sensor_serial = serializers.CharField(source='sensor.sensor_number', read_only=True)

    class Meta:
        model = SensorReading
        fields = [
            'id',
            'station',
            'station_code',
            'sensor',
            'sensor_serial',
            'water_level',
            'signal_strength',
            'battery_level_snapshot',
            'timestamp'
        ]