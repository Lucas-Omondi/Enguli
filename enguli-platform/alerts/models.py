from django.db import models
from stations.models import Station, Sensor


class Alert(models.Model):

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)

    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)

    alert_type = models.CharField(max_length=100)  # e.g. WATER_LEVEL_HIGH

    message = models.TextField()

    is_resolved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']