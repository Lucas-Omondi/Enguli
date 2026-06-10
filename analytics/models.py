from django.db import models
from stations.models import Station


class StationReadingAggregate(models.Model):
    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='aggregates'
    )

    average_water_level = models.FloatField()
    min_water_level = models.FloatField()
    max_water_level = models.FloatField()

    std_deviation = models.FloatField(default=0.0)

    confidence_score = models.FloatField(default=1.0)

    reading_count = models.IntegerField()

    time_window_start = models.DateTimeField()
    time_window_end = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-time_window_end']