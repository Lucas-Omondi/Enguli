from django.urls import path
from .views import StationAnalyticsView, SandDamStorageModelView

urlpatterns = [
    path('stations/<int:station_id>/', StationAnalyticsView.as_view(), name='station_analytics'),
    path('storage-model/', SandDamStorageModelView.as_view(), name='sand_dam_storage_model'),
]