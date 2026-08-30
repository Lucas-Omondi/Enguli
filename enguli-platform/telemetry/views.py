import csv
import traceback
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
        try:
            serializer = SensorIngestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            serial = data['resolved_serial']
            raw_distance = data['resolved_distance']
            stn_id = data.get('station_id')
            stn_code = data.get('station_code')

            # 1. Resolve Target Station from ESP32 payload
            target_station = None
            if stn_id is not None:
                target_station = Station.objects.filter(id=stn_id).first()

            if not target_station and stn_code:
                target_station = Station.objects.filter(station_code__iexact=str(stn_code).strip()).first()

            # Fallback to the first station in the database if not matched
            station = target_station or Station.objects.first()

            if not station:
                return Response(
                    {"error": "No station found in database. Create a Station in Django Admin first."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 2. Fetch or Auto-Register Sensor with the resolved station
            try:
                sensor, created = Sensor.objects.select_related('station').get_or_create(
                    serial_number=serial,
                    defaults={
                        'station': station,
                        'calibration_offset': 3.0,
                        'status': 'ACTIVE'
                    }
                )
            except Exception as sensor_err:
                print(f"[Sensor Auto-Registration Notice]: {sensor_err}")
                sensor = Sensor.objects.filter(serial_number=serial).first()
                if not sensor:
                    raise sensor_err
                created = False

            # If station was explicitly passed and differs from sensor's current station, update it
            if target_station and sensor.station != target_station:
                sensor.station = target_station
                try:
                    sensor.save(update_fields=['station'])
                except Exception:
                    sensor.save()

            active_station = sensor.station or station

            # 3. Calibration: Water Depth = Sensor Mounting Datum Offset - Measured Distance
            offset = getattr(sensor, 'calibration_offset', 3.0)
            if offset is None:
                offset = 3.0
            calibrated_depth = offset - raw_distance

            # 4. Save Reading Record
            reading = SensorReading.objects.create(
                sensor=sensor,
                station=active_station,
                water_level=calibrated_depth,
                battery_level_snapshot=data.get('battery_level'),
                signal_strength=data.get('signal_strength'),
            )

            # 5. Update sensor diagnostics safely
            if data.get('battery_level') is not None and hasattr(sensor, 'battery_level'):
                sensor.battery_level = data['battery_level']
                try:
                    sensor.save(update_fields=['battery_level'])
                except Exception:
                    sensor.save()

            # 6. Trigger Alerts safely
            try:
                generate_alert(sensor, active_station, reading)
            except Exception as alert_err:
                print(f"[Alert Processing Warning]: {alert_err}")

            return Response({
                "message": "Reading processed successfully",
                "auto_registered": created,
                "station_id": active_station.id,
                "station_code": getattr(active_station, 'station_code', str(active_station)),
                "sensor": sensor.serial_number,
                "raw_distance_mean": round(raw_distance, 3),
                "water_level": round(reading.water_level, 3)
            }, status=status.HTTP_201_CREATED)

        except Exception as err:
            traceback.print_exc()
            return Response(
                {
                    "error_type": type(err).__name__,
                    "error_detail": str(err)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


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
            'Station ID',
            'Station Code',
            'Station Name',
            'Sensor Serial',
            'Water Level (m)',
            'Battery Level (%)',
            'Signal Strength (RSSI)',
            'Timestamp (UTC)'
        ])

        for log in queryset[:5000]:
            writer.writerow([
                log.id,
                log.station.id if log.station else '',
                log.station.station_code if log.station else 'N/A',
                log.station.station_name if log.station else 'N/A',
                log.sensor.serial_number if log.sensor else 'N/A',
                round(log.water_level, 3) if log.water_level is not None else '',
                log.battery_level_snapshot if log.battery_level_snapshot is not None else '',
                log.signal_strength if log.signal_strength is not None else '',
                log.timestamp.isoformat() if log.timestamp else ''
            ])

        return response