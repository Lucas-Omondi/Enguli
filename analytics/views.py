from rest_framework.views import APIView
from rest_framework.response import Response

from stations.models import Station
from .services import get_station_aggregation


class StationAnalyticsView(APIView):

    def get(self, request, station_id):
        try:
            station = Station.objects.get(id=station_id)
        except Station.DoesNotExist:
            return Response({"error": "Station not found"}, status=404)

        data = get_station_aggregation(station_id)

        return Response({
            "station": station.station_code,
            "average_water_level": data["average_water_level"],
            "min_water_level": data["min_water_level"],
            "max_water_level": data["max_water_level"],
            "reading_count": data["reading_count"]
        })