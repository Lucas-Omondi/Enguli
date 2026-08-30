import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, viewsets
from stations.models import Sensor, Station
from .models import SensorReading
from .serializers import SensorIngestSerializer, SensorReadingSerializer
from alerts.services import generate_alert


class TelemetryIngestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SensorIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        serial = data['resolved_serial']
        raw_distance = data['resolved_distance']

        # Ensure a station exists
        default_station = Station.objects.first()
        if not default_station:
            return Response(
                {"error": "No station found in database. Create at least one Station in Django Admin first."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 1. Fetch or automatically register the sensor
        sensor, created = Sensor.objects.select_related('station').get_or_create(
            serial_number=serial,
            defaults={
                'station': default_station,
                'calibration_offset': 3.0,  # Default reference height in meters
                'status': 'ACTIVE'
            }
        )

        station = sensor.station or default_station

        # 2. Calibration: Water Depth = Total Height - Distance to Water Surface
        offset = sensor.calibration_offset if sensor.calibration_offset is not None else 3.0
        calibrated_depth = offset - raw_distance

        # 3. Store reading
        reading = SensorReading.objects.create(
            sensor=sensor,
            station=station,
            water_level=calibrated_depth,
            battery_level_snapshot=data.get('battery_level'),
            signal_strength=data.get('signal_strength'),
        )

        # 4. Update sensor diagnostics
        if data.get('battery_level') is not None:
            sensor.battery_level = data['battery_level']
            # Fall back to save() safely if updated_at is not defined on the model
            try:
                sensor.save(update_fields=['battery_level', 'updated_at'])
            except Exception:
                sensor.save(update_fields=['battery_level'])

        # 5. Alert Trigger
        try:
            generate_alert(sensor, station, reading)
        except Exception as e:
            print(f"Alert error: {e}")

        return Response({
            "message": "Reading processed successfully",
            "auto_registered": created,
            "station": getattr(station, 'station_code', str(station)),
            "sensor": sensor.serial_number,
            "water_level": reading.water_level
        }, status=status.HTTP_201_CREATED)


class SensorReadingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Exposes a read-only endpoint to stream historical logs
    and time-series data to frontend tables and charts.
    """
    queryset = SensorReading.objects.select_related('station', 'sensor').all().order_by('-timestamp')
    serializer_class = SensorReadingSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        station_id = self.request.query_params.get('station_id')
        if station_id:
            queryset = queryset.filter(station_id=station_id)

        return queryset


class ExportTelemetryCSVView(APIView):
    """
    Exports telemetry time-series records to CSV format for hydrological reporting.
    Accepts optional filters: ?station_id=X, ?start_date=YYYY-MM-DD, ?end_date=YYYY-MM-DD
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        station_id = request.query_params.get('station_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        queryset = SensorReading.objects.select_related('station', 'sensor').all().order_by('-timestamp')

        if station_id:
            queryset = queryset.filter(station_id=station_id)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="enguli_telemetry_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Log ID',
            'Station Code',
            'Station Name',
            'Sensor Serial',
            'Water Level (m)',
            'Battery Level (%)',
            'Signal Strength (RSSI)',
            'Timestamp (UTC)'
        ])

        # Capped to 5,000 rows for high performance
        for log in queryset[:5000]:
            writer.writerow([
                log.id,
                log.station.station_code if log.station else 'N/A',
                log.station.station_name if log.station else 'N/A',
                log.sensor.serial_number if log.sensor else 'N/A',
                round(log.water_level, 3) if log.water_level is not None else '',
                log.battery_level_snapshot if log.battery_level_snapshot is not None else '',
                log.signal_strength if log.signal_strength is not None else '',
                log.timestamp.isoformat() if log.timestamp else ''
            ])

        return response