from django.contrib import admin
from .models import Ride, RideEvent

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'rider', 'driver', 'status', 'start_time', 'end_time')
    list_filter = ('status', 'start_time')
    search_fields = ('rider__username', 'driver__username', 'start_location', 'end_location')
    ordering = ('-start_time',)

@admin.register(RideEvent)
class RideEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'ride', 'timestamp', 'description')
    list_filter = ('timestamp',)
    search_fields = ('ride__id', 'description')
