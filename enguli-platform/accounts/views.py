from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserDetailSerializer
from .permissions import IsAdminOrFieldEngineer


class CurrentUserView(APIView):
    """
    Returns the authenticated user's profile and assigned role.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    List registered users and create new accounts with roles.
    """
    queryset = User.objects.select_related('profile').all().order_by('-date_joined')
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrFieldEngineer]

    def create(self, request, *args, **kwargs):
        data = request.data
        username = data.get('username')
        email = data.get('email', '')
        password = data.get('password')
        role = data.get('role', 'OBSERVER')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        phone_number = data.get('phone_number', '')

        if not username or not password:
            return Response(
                {"detail": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"detail": "A user with that username already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.phone_number = phone_number
        profile.save()

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)