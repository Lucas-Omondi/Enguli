from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Station(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
    ]

    station_code = models.CharField(max_length=50, unique=True)
    station_name = models.CharField(max_length=255)

    latitude = models.FloatField()
    longitude = models.FloatField()

    location_description = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    # Real-time heartbeat tracking
    last_seen = models.DateTimeField(null=True, blank=True)
    offline_threshold_seconds = models.PositiveIntegerField(default=75)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_online(self) -> bool:
        if not self.last_seen:
            return False
        cutoff = timezone.now() - timedelta(seconds=self.offline_threshold_seconds)
        return self.last_seen >= cutoff

    @property
    def connection_status(self) -> str:
        return "ONLINE" if self.is_online else "UNAVAILABLE"

    def __str__(self):
        return f"{self.station_code} - {self.station_name}"


class Sensor(models.Model):
    SENSOR_TYPES = [
        ('ultrasonic', 'Ultrasonic'),
        ('pressure', 'Pressure'),
    ]

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name='sensors'
    )
    sensor_code = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    sensor_type = models.CharField(max_length=50, choices=SENSOR_TYPES)
    serial_number = models.CharField(max_length=100, unique=True)

    battery_level = models.FloatField(default=100)
    connectivity_status = models.BooleanField(default=True)

    calibration_offset = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_online(self) -> bool:
        # Inherits live connectivity from the parent ESP32 station node
        return self.station.is_online

    @property
    def connection_status(self) -> str:
        return "ONLINE" if self.is_online else "UNAVAILABLE"

    def __str__(self):
        return f"{self.sensor_code} ({self.serial_number})"