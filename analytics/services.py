from django.db.models import Avg, Min, Max, Count
from telemetry.models import SensorReading


def get_station_aggregation(station_id):
    readings = SensorReading.objects.filter(station_id=station_id)

    return readings.aggregate(
        average_water_level=Avg('water_level'),
        min_water_level=Min('water_level'),
        max_water_level=Max('water_level'),
        reading_count=Count('id')
    )