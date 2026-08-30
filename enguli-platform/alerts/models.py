from django.db import models
from stations.models import Station, Sensor


class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='alerts')
    sensor = models.ForeignKey(Sensor, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')

    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    alert_type = models.CharField(max_length=100)  # e.g. LOW_BATTERY, RAPID_DRAWDOWN, SENSOR_OFFLINE

    message = models.TextField()
    is_resolved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.severity.upper()}] {self.station.station_code} - {self.alert_type}"