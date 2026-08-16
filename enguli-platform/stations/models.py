from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'System Administrator'),
        ('FIELD_ENGINEER', 'Field Engineer'),
        ('OBSERVER', 'Observer / Farmer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='OBSERVER')
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Default superusers to ADMIN, regular users to OBSERVER
        default_role = 'ADMIN' if instance.is_superuser else 'OBSERVER'
        UserProfile.objects.create(user=instance, role=default_role)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    def __str__(self):
        return f"{self.sensor_code} ({self.serial_number})"