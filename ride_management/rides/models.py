from django.db import models
from users.models import User
from django.utils.timezone import now

class Ride(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    rider = models.ForeignKey(
        User, 
        related_name='rides_as_rider', 
        on_delete=models.CASCADE
    )
    driver = models.ForeignKey(
        User, 
        related_name='rides_as_driver', 
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='scheduled'
    )
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=now)  # Ajout de la date de création
    updated_at = models.DateTimeField(default=now)  # Ajout de la date de mise à jour

    def __str__(self):
        return f"Ride {self.id} - {self.status}"

    class Meta:
        ordering = ['-start_time']

    def save(self, *args, **kwargs):
        # Detect if the status is changed to 'in_progress' or 'completed'
        if self.pk:  # Ensure this is an update, not a new creation
            previous_status = Ride.objects.get(pk=self.pk).status
            if self.status == 'in_progress' and previous_status != 'in_progress':
                self.start_time = now()  # Set start time to the current time
                self.driver.is_available = False  # Mark the driver as unavailable
                self.driver.save()
            elif self.status == 'completed' and previous_status != 'completed':
                self.end_time = now()  # Set end time to the current time
                self.driver.is_available = True  # Mark the driver as available
                self.driver.save()

        # Call the original save method
        super().save(*args, **kwargs)



class RideEvent(models.Model):
    ride = models.ForeignKey(
        Ride, 
        related_name='events', 
        on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"Event for Ride {self.ride.id} - {self.timestamp}"
