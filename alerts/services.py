from .models import Alert


def generate_alert(sensor, station, reading):
    water_level = reading.water_level
    battery = reading.battery_level_snapshot

    # HIGH WATER LEVEL
    if water_level >= 4.0:
        Alert.objects.create(
            station=station,
            sensor=sensor,
            severity='critical',
            alert_type='WATER_LEVEL_CRITICAL',
            message=f"Critical water level detected: {water_level}m"
        )

    elif water_level >= 3.0:
        Alert.objects.create(
            station=station,
            sensor=sensor,
            severity='high',
            alert_type='WATER_LEVEL_HIGH',
            message=f"High water level detected: {water_level}m"
        )

    # LOW BATTERY
    if battery is not None and battery < 20:
        Alert.objects.create(
            station=station,
            sensor=sensor,
            severity='medium',
            alert_type='LOW_BATTERY',
            message=f"Sensor battery low: {battery}%"
        )