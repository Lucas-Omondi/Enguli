from rest_framework import serializers
from .models import SensorReading


class SensorIngestSerializer(serializers.Serializer):
    # Support both key conventions from hardware and API calls
    sensor_serial = serializers.CharField(required=False, allow_blank=True)
    serial_number = serializers.CharField(required=False, allow_blank=True)

    # Support both raw distance from ESP32 and direct water level
    raw_distance = serializers.FloatField(required=False)
    water_level = serializers.FloatField(required=False)

    # Diagnostics
    battery_level = serializers.FloatField(required=False, allow_null=True)
    signal_strength = serializers.FloatField(required=False, allow_null=True)

    def validate(self, attrs):
        # 1. Resolve and validate serial number
        serial = attrs.get('sensor_serial') or attrs.get('serial_number')
        if not serial:
            raise serializers.ValidationError({
                "serial_number": "Either 'sensor_serial' or 'serial_number' is required."
            })
        attrs['resolved_serial'] = serial

        # 2. Resolve and validate distance / water level reading
        reading = attrs.get('raw_distance') if attrs.get('raw_distance') is not None else attrs.get('water_level')
        if reading is None:
            raise serializers.ValidationError({
                "raw_distance": "Either 'raw_distance' or 'water_level' is required."
            })
        attrs['resolved_distance'] = reading

        return attrs


class SensorReadingSerializer(serializers.ModelSerializer):
    station_code = serializers.CharField(source='station.station_code', read_only=True)
    # Fixed: points to serial_number instead of sensor_number
    sensor_serial = serializers.CharField(source='sensor.serial_number', read_only=True)

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