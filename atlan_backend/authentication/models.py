from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

class Driver(models.Model):
    DRIVER_STATUS_CHOICES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('on_trip', 'On Trip')
    ]
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    license_number = models.CharField(max_length=50, unique=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='available', choices=DRIVER_STATUS_CHOICES)
    availability_status = models.BooleanField(default=True)
    fleet_owner = models.ForeignKey('FleetOwner', on_delete=models.CASCADE, null=True, blank=True)

class FleetOwner(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    registration_date = models.DateTimeField(auto_now_add=True)