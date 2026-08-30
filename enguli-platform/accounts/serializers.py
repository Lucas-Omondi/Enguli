from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role', 'phone_number']


class UserDetailSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_superuser', 'profile']

    def get_profile(self, obj):
        # Gracefully handle users without a profile
        if hasattr(obj, 'profile'):
            return UserProfileSerializer(obj.profile).data
        return {
            'role': 'ADMIN' if obj.is_superuser else 'OBSERVER',
            'phone_number': ''
        }