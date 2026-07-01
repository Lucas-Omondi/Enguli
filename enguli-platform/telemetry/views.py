from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from stations.models import Sensor
from .models import SensorReading
from .serializers import SensorIngestSerializer, SensorReadingSerializer
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

        #CALIBRATION
        # Assumes hardware sends raw distance (D) from sensor lens to water surface.
        # sensor.calibration_offset represents total height (H) from lens to well base.
        raw_distance = data['water_level']
        calibrated_water_table_depth = sensor.calibration_offset - raw_distance

        # 3. Store calibrated reading
        reading = SensorReading.objects.create(
            sensor=sensor,
            station=station,
            water_level=calibrated_water_table_depth,  # Saved as actual aquifer depth
            battery_level_snapshot=data.get('battery_level'),
            signal_strength=data.get('signal_strength'),
        )

        # Update the master sensor diagnostic
        if data.get('battery_level') is not None:
            sensor.battery_level = data['battery_level']
            sensor.save(update_fields=['battery_level', 'updated_at'])

        # 4. TRIGGER ALERT ENGINE
        try:
            generate_alert(sensor, station, reading)
        except Exception as e:
            # IMPORTANT: ingestion must NOT fail if alerts fail
            print(f"Alert error: {e}")

        # 5. Response
        return Response(
            {
                "message": "Reading stored and calibrated successfully",
                "station": station.station_code,
                "sensor": sensor.serial_number,
                "water_level": reading.water_level  # Returns calibrated value
            },
            status=status.HTTP_201_CREATED
        )


class SensorReadingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Exposes a read-only endpoint to stream historical logs
    and time-series data to frontend tables and charts.
    """
    # Use select_related to optimize database execution queries
    queryset = SensorReading.objects.select_related('station', 'sensor').all().order_by('-timestamp')
    serializer_class = SensorReadingSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Allows your Vue frontend to pass ?station_id=X to filter records
        station_id = self.request.query_params.get('station_id')
        if station_id:
            queryset = queryset.filter(station_id=station_id)

        return queryset