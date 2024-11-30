from django import forms
from .models import Ride
from users.models import User
from django.utils.timezone import now
from django.db.models import Q
import logging
logger = logging.getLogger(__name__)



class RideCreateForm(forms.ModelForm):
    """
    Form for creating a new ride.
    Filters drivers to include only those who are available (completed rides or no rides).
    """
    class Meta:
        model = Ride
        fields = [
            'driver', 'status',
            'pickup_latitude', 'pickup_longitude',
            'dropoff_latitude', 'dropoff_longitude',
            'start_time'
        ]
        widgets = {
            'driver': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'pickup_latitude': forms.TextInput(attrs={'class': 'form-control'}),
            'pickup_longitude': forms.TextInput(attrs={'class': 'form-control'}),
            'dropoff_latitude': forms.TextInput(attrs={'class': 'form-control'}),
            'dropoff_longitude': forms.TextInput(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter drivers: only those with completed rides or no rides
        self.fields['driver'].queryset = User.objects.filter(
            role='driver'
        ).exclude(
            rides_as_driver__status='in_progress'
        ).distinct()

        # Prefill the start_time field
        self.fields['start_time'].initial = now().strftime('%Y-%m-%dT%H:%M')


class RideUpdateForm(forms.ModelForm):
    """
    Form for updating an existing ride.
    Filters drivers based on the ride's current status.
    Dynamically marks fields as readonly.
    """
    class Meta:
        model = Ride
        fields = [
            'driver', 'status',
            'pickup_latitude', 'pickup_longitude',
            'dropoff_latitude', 'dropoff_longitude',
            'start_time'
        ]
        widgets = {
            'driver': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'pickup_latitude': forms.TextInput(attrs={'class': 'form-control'}),
            'pickup_longitude': forms.TextInput(attrs={'class': 'form-control'}),
            'dropoff_latitude': forms.TextInput(attrs={'class': 'form-control'}),
            'dropoff_longitude': forms.TextInput(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        ride_instance = kwargs.get('instance')  # Get the current ride instance
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Read-only fields tracking
        self.readonly_fields = []

        if ride_instance:
            if ride_instance.status == 'scheduled':
                # Allow selecting any available driver (completed rides or no rides)
                self.fields['driver'].queryset = User.objects.filter(
                    role='driver'
                ).exclude(
                    rides_as_driver__status='in_progress'
                ).distinct()
            elif ride_instance.status == 'in_progress':
                # Only include the current driver and mark as readonly
                self.fields['driver'].queryset = User.objects.filter(
                    id=ride_instance.driver.id
                )
                self.fields['driver'].widget.attrs['readonly'] = True
                self.readonly_fields.append('driver')

            # Mark fields as readonly for specific statuses
            if ride_instance.status in ['in_progress', 'completed']:
                self.fields['pickup_latitude'].widget.attrs['readonly'] = True
                self.fields['pickup_longitude'].widget.attrs['readonly'] = True
                self.fields['start_time'].widget.attrs['readonly'] = True
                self.readonly_fields.extend(['pickup_latitude', 'pickup_longitude', 'start_time'])

    # def clean(self):
    #     cleaned_data = super().clean()

    #     # Retain values for readonly fields
    #     for field in self.readonly_fields:
    #         if field in self.fields:
    #             cleaned_data[field] = getattr(self.instance, field)

    #     return cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        logger.debug(f"Readonly fields: {self.readonly_fields}")
        logger.debug(f"Cleaned data before retaining readonly: {cleaned_data}")

        for field in self.readonly_fields:
            if field in self.fields:
                cleaned_data[field] = getattr(self.instance, field)

        logger.debug(f"Cleaned data after retaining readonly: {cleaned_data}")
        return cleaned_data

