from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('driver', 'Driver'),
        ('rider', 'Rider'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='rider')

    def __str__(self):
        return self.username

    @property
    def is_driver(self):
        return self.role == 'driver'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_rider(self):
        return self.role == 'rider'

