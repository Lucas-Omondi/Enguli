from rest_framework import serializers
from .models import SensorReading


from rest_framework import serializers
from .models import SensorReading


class SensorIngestSerializer(serializers.Serializer):
    # Support multiple serial key conventions
    sensor_serial = serializers.CharField(required=False, allow_blank=True)
    serial_number = serializers.CharField(required=False, allow_blank=True)

    # Dual sensor inputs from ESP32
    raw_distance_1 = serializers.FloatField(required=False, allow_null=True)
    raw_distance_2 = serializers.FloatField(required=False, allow_null=True)

    # Single sensor fallback / direct water level input
    raw_distance = serializers.FloatField(required=False, allow_null=True)
    water_level = serializers.FloatField(required=False, allow_null=True)

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

        # 2. Extract distance inputs
        d1 = attrs.get('raw_distance_1')
        d2 = attrs.get('raw_distance_2')
        raw = attrs.get('raw_distance')
        wl = attrs.get('water_level')

        # Filter valid positive dual-sensor readings
        valid_readings = [d for d in [d1, d2] if d is not None and d > 0]

        # 3. Backend Averaging and Selection Logic
        if valid_readings:
            # Django calculates mean of active sensors
            resolved_dist = sum(valid_readings) / len(valid_readings)
        elif raw is not None and raw > 0:
            resolved_dist = raw
        elif wl is not None:
            resolved_dist = wl
        else:
            raise serializers.ValidationError({
                "raw_distance": "At least one valid sensor reading (raw_distance_1, raw_distance_2, or raw_distance) is required."
            })

        attrs['resolved_distance'] = resolved_dist
        return attrs


class SensorReadingSerializer(serializers.ModelSerializer):
    station_code = serializers.CharField(source='station.station_code', read_only=True)
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

