from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from stations.models import Station
from .services import get_station_aggregation


class StationAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, station_id):
        try:
            station = Station.objects.get(id=station_id)
        except Station.DoesNotExist:
            return Response({"error": "Station not found"}, status=status.HTTP_404_NOT_FOUND)

        data = get_station_aggregation(station_id)

        return Response({
            "station": station.station_code,
            "average_water_level": data["average_water_level"],
            "min_water_level": data["min_water_level"],
            "max_water_level": data["max_water_level"],
            "reading_count": data["reading_count"]
        })


class SandDamStorageModelView(APIView):
    """
    Sand Dam Volumetric Hydrological Storage Model:
    Calculates active saturated sand storage volume (m^3) and days of water reserve remaining.
    Formula: V_extractable = Length * Width * (Bed_Depth - Water_Table_Depth) * Specific_Yield
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        station_id = request.data.get('station_id')
        if not station_id:
            return Response({"error": "station_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            station = Station.objects.get(id=station_id)
        except Station.DoesNotExist:
            return Response({"error": "Station not found."}, status=status.HTTP_404_NOT_FOUND)

        # Reservoir Geometry & Hydrological Parameters (with realistic defaults)
        try:
            length = float(request.data.get('length_m', 250.0))         # Length of sand reservoir along channel (m)
            width = float(request.data.get('width_m', 20.0))            # Average sand bed width (m)
            bed_depth = float(request.data.get('bed_depth_m', 4.5))     # Total sand thickness to impermeable bedrock (m)
            specific_yield = float(request.data.get('specific_yield', 0.28)) # Drainable porosity (Sy: 0.25 - 0.35 for coarse river sand)
            daily_demand = float(request.data.get('daily_demand_m3', 50.0))  # Daily community/irrigation extraction rate (m^3/day)
        except (ValueError, TypeError):
            return Response({"error": "Invalid numerical parameters supplied."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve latest water depth telemetry for this station
        latest_telemetry = TelemetryData.objects.filter(sensor__station=station).order_by('-timestamp').first()

        if latest_telemetry and latest_telemetry.water_level is not None:
            water_table_depth = float(latest_telemetry.water_level)
            reading_time = latest_telemetry.timestamp
        else:
            # Fallback if no telemetry is logged yet (assumes midpoint)
            water_table_depth = bed_depth * 0.5
            reading_time = None

        # Saturated thickness calculation (clamped between 0 and total bed depth)
        saturated_thickness = max(0.0, min(bed_depth, bed_depth - water_table_depth))

        # Storage capacity computations
        total_sand_volume = length * width * bed_depth
        max_storage_capacity_m3 = total_sand_volume * specific_yield
        current_extractable_volume_m3 = (length * width * saturated_thickness) * specific_yield

        percentage_full = (current_extractable_volume_m3 / max_storage_capacity_m3 * 100) if max_storage_capacity_m3 > 0 else 0.0
        estimated_days_remaining = (current_extractable_volume_m3 / daily_demand) if daily_demand > 0 else 0.0

        return Response({
            "station_id": station.id,
            "station_code": station.station_code,
            "station_name": station.station_name,
            "last_reading_time": reading_time,
            "parameters_used": {
                "length_m": length,
                "width_m": width,
                "bed_depth_m": bed_depth,
                "specific_yield": specific_yield,
                "daily_demand_m3": daily_demand
            },
            "hydrology_metrics": {
                "water_table_depth_m": round(water_table_depth, 2),
                "saturated_thickness_m": round(saturated_thickness, 2),
                "total_sand_volume_m3": round(total_sand_volume, 1),
                "max_storage_capacity_m3": round(max_storage_capacity_m3, 1),
                "current_extractable_volume_m3": round(current_extractable_volume_m3, 1),
                "percentage_full": round(percentage_full, 1),
                "estimated_days_remaining": round(estimated_days_remaining, 1)
            }
        }, status=status.HTTP_200_OK)