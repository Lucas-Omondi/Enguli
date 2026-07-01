from django.urls import path
from .views import StationAnalyticsView

urlpatterns = [
    path('stations/<int:station_id>/', StationAnalyticsView.as_view()),
]