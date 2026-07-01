from .models import Alert


def generate_alert(sensor, station, reading):
    water_level = reading.water_level
    battery = reading.battery_level_snapshot

    # Check for critical high water / flash floods
    if water_level >= 4.0:
        # Look for an existing unresolved critical alert
        exists = Alert.objects.filter(
            station=station,
            alert_type='WATER_LEVEL_CRITICAL',
            is_resolved=False
        ).exists()

        # Only create if one does not already exist
        if not exists:
            Alert.objects.create(
                station=station,
                sensor=sensor,
                severity='critical',
                alert_type='WATER_LEVEL_CRITICAL',
                message=f"Critical water level detected: {water_level}m"
            )

    # Check for high water alerts
    elif water_level >= 3.0:
        exists = Alert.objects.filter(
            station=station,
            alert_type='WATER_LEVEL_HIGH',
            is_resolved=False
        ).exists()

        if not exists:
            Alert.objects.create(
                station=station,
                sensor=sensor,
                severity='high',
                alert_type='WATER_LEVEL_HIGH',
                message=f"High water level detected: {water_level}m"
            )

    # Check for low water alerts to assist irrigation management
    elif water_level <= 0.5:
        exists = Alert.objects.filter(
            station=station,
            alert_type='WATER_LEVEL_LOW',
            is_resolved=False
        ).exists()

        if not exists:
            Alert.objects.create(
                station=station,
                sensor=sensor,
                severity='high',
                alert_type='WATER_LEVEL_LOW',
                message=f"Low water level warning: {water_level}m. Optimize abstraction."
            )

    # Check for hardware battery levels
    if battery is not None and battery < 20:
        exists = Alert.objects.filter(
            sensor=sensor,
            alert_type='LOW_BATTERY',
            is_resolved=False
        ).exists()

        if not exists:
            Alert.objects.create(
                station=station,
                sensor=sensor,
                severity='medium',
                alert_type='LOW_BATTERY',
                message=f"Sensor battery low: {battery}%"
            )