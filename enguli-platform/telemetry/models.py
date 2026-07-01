from django.db import models
from stations.models import Station, Sensor


class SensorReading(models.Model):
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='readings'
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='readings'
    )

    water_level = models.FloatField()

    signal_strength = models.FloatField(null=True, blank=True)

    battery_level_snapshot = models.FloatField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.station.station_code} - {self.water_level}"