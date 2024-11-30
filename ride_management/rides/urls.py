from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# API Routes
router = DefaultRouter()
router.register(r'rides', RideViewSet, basename='ride')
router.register(r'ride-events', RideEventViewSet, basename='ride-event')

# UI Routes for Rides
urlpatterns = [
    # API Endpoints
    path('', include(router.urls)),
    path('reports/trips-over-one-hour/', TripDurationReportView.as_view(), name='trip_duration_report'),
    path('rides/<int:pk>/update/', RideUpdateView.as_view(), name='ride-update'),

    # UI Endpoints
    path('ui/rides/', RideListView.as_view(), name='ride-list'),
    path('ui/rides/create/', RideCreateView.as_view(), name='ride-create'),
    path('ui/rides/<int:pk>/', RideDetailView.as_view(), name='ride-detail'),
    path('ui/rides/<int:pk>/update/', RideUpdateView.as_view(), name='ride-update'),
]
