from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from stations.models import Sensor
from .models import SensorReading
from .serializers import SensorIngestSerializer
from alerts.services import generate_alert


class TelemetryIngestView(APIView):

    def post(self, request):
        serializer = SensorIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # 1. Find sensor by serial number
        try:
            sensor = Sensor.objects.select_related('station').get(
                serial_number=data['sensor_serial']
            )
        except Sensor.DoesNotExist:
            return Response(
                {"error": "Sensor not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Get station
        station = sensor.station

        # 3. Store raw reading
        reading = SensorReading.objects.create(
            sensor=sensor,
            station=station,
            water_level=data['water_level'],
            battery_level_snapshot=data.get('battery_level'),
            signal_strength=data.get('signal_strength'),
        )

        # 4. 🔥 TRIGGER ALERT ENGINE (NEW STEP)
        try:
            generate_alert(sensor, station, reading)
        except Exception as e:
            # IMPORTANT: ingestion must NOT fail if alerts fail
            print(f"Alert error: {e}")

        # 5. Response
        return Response(
            {
                "message": "Reading stored successfully",
                "station": station.station_code,
                "sensor": sensor.serial_number,
                "water_level": reading.water_level
            },
            status=status.HTTP_201_CREATED
        )