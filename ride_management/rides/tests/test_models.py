from django.test import TestCase
from django.utils.timezone import make_aware
from datetime import datetime
from users.models import User
from rides.models import Ride, RideEvent
from users.models import User

class RideModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_user", role="driver")
        self.ride = Ride.objects.create(
            rider=self.user,
            driver=self.user,
            status="scheduled",
            pickup_latitude=37.7749,
            pickup_longitude=-122.4194,
            dropoff_latitude=37.8044,
            dropoff_longitude=-122.2712,
            start_location="Location A",
            end_location="Location B",
            start_time=make_aware(datetime(2024, 1, 1, 10, 0, 0))
        )

    def test_ride_creation(self):
        self.assertEqual(self.ride.status, "scheduled")

    def test_event_creation(self):
        event = RideEvent.objects.create(ride=self.ride, description="Ride started")
        self.assertEqual(event.description, "Ride started")




class UserModelTest(TestCase):
    def test_user_roles(self):
        admin = User.objects.create_user(username="admin", password="admin123", role="admin")
        driver = User.objects.create_user(username="driver", password="driver123", role="driver")
        rider = User.objects.create_user(username="rider", password="rider123", role="rider")

        self.assertTrue(admin.is_admin)
        self.assertTrue(driver.is_driver)
        self.assertTrue(rider.is_rider)
