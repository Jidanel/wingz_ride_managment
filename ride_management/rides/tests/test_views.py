from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils.timezone import make_aware
from datetime import datetime
from users.models import User
from rides.models import Ride

class RideAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create an admin user
        self.admin_user = User.objects.create_user(
            username="admin",
            password="admin123"
        )
        self.admin_user.role = "admin"  # Explicitly set the role to admin
        self.admin_user.save()

        # Create a rider user
        self.rider = User.objects.create_user(username="rider", password="rider123", role="rider")

        # Create a driver user
        self.driver = User.objects.create_user(username="driver", password="driver123", role="driver")

        # Create a ride
        self.ride = Ride.objects.create(
            rider=self.rider,
            driver=self.driver,
            status="scheduled",
            start_location="Location A",
            end_location="Location B",
            pickup_latitude=37.7749,
            pickup_longitude=-122.4194,
            dropoff_latitude=37.8044,
            dropoff_longitude=-122.2712,
            start_time=make_aware(datetime(2024, 1, 1, 10, 0, 0))
        )

    def authenticate_admin(self):
        """Authenticate as admin user."""
        self.client.force_authenticate(user=self.admin_user)

    def test_list_rides_authenticated(self):
        self.authenticate_admin()
        response = self.client.get('/api/rides/rides/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #self.assertEqual(len(response.data['results']), 1)

    def test_create_ride(self):
        self.authenticate_admin()
        data = {
            "rider": self.rider.id,
            "driver": self.driver.id,
            "status": "scheduled",
            "start_location": "New Location A",
            "end_location": "New Location B",
            "pickup_latitude": 37.7749,
            "pickup_longitude": -122.4194,
            "dropoff_latitude": 37.8044,
            "dropoff_longitude": -122.2712,
            "start_time": "2024-01-02T10:00:00Z",
        }
        response = self.client.post('/api/rides/rides/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_sort_by_distance(self):
        """
        Teste le tri des trajets par distance à partir d'une position GPS donnée.
        """
        self.authenticate_admin()
        response = self.client.get('/api/rides/rides/', {
            'latitude': 37.7750, 
            'longitude': -122.4195,
            'order_by': 'distance'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Vérification des champs de distance
        self.assertIn('distance', response.data['results'][0])
        self.assertGreater(response.data['results'][0]['distance'], 0)


    def test_sort_by_distance_multiple_rides(self):
        """
        Teste le tri des trajets par distance à partir d'une position GPS donnée.
        """
        self.authenticate_admin()

        # Ajouter un autre trajet
        Ride.objects.create(
            rider=self.rider,
            driver=self.driver,
            status="scheduled",
            start_location="Location C",
            end_location="Location D",
            pickup_latitude=37.8044,
            pickup_longitude=-122.2712,
            dropoff_latitude=37.8715,
            dropoff_longitude=-122.2730,
            start_time=make_aware(datetime(2024, 1, 2, 10, 0, 0))
        )

        response = self.client.get('/api/rides/rides/', {
            'latitude': 37.7750,
            'longitude': -122.4195,
            'order_by': 'distance'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']

        # Vérifier que les distances sont triées
        self.assertGreater(results[1]['distance'], results[0]['distance'])
