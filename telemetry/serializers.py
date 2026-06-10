from rest_framework import serializers


class SensorIngestSerializer(serializers.Serializer):
    sensor_serial = serializers.CharField()
    water_level = serializers.FloatField()
    battery_level = serializers.FloatField(required=False)
    signal_strength = serializers.FloatField(required=False)