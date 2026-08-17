from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'System Administrator'),
        ('FIELD_ENGINEER', 'Field Engineer'),
        ('OBSERVER', 'Farmer / Basin Observer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='OBSERVER')
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        default_role = 'ADMIN' if instance.is_superuser else 'OBSERVER'
        UserProfile.objects.create(user=instance, role=default_role)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()