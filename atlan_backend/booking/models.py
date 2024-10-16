from django.db import models
from django.conf import settings
from django.apps import apps

from vehicle_type.models import VehicleType
from pricing_model.models import PricingModel
import random

class Location(models.Model):
    PICKUP = 'pickup'
    DROPOFF = 'dropoff'
    LOCATION_TYPE_CHOICES = [
        (PICKUP, 'Pickup'),
        (DROPOFF, 'Dropoff'),
    ]

    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=7)
    longitude = models.DecimalField(max_digits=9, decimal_places=7)
    place_name = models.CharField(max_length=255)
    location_type = models.CharField(max_length=10, choices=LOCATION_TYPE_CHOICES)

    def __str__(self):
        return f"{self.place_name} ({self.address})"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('on_trip', 'On Trip'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    driver = models.ForeignKey('authentication.Driver', on_delete=models.SET_NULL, null=True, blank=True)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    pickup_location = models.ForeignKey(Location, related_name='pickup_bookings', on_delete=models.CASCADE)
    dropoff_location = models.ForeignKey(Location, related_name='dropoff_bookings', on_delete=models.CASCADE)
    pricing = models.ForeignKey(PricingModel, on_delete=models.SET_NULL, null=True, blank=True)
    booking_time = models.DateTimeField(auto_now_add=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    pickup_time = models.DateTimeField(null=True, blank=True)
    dropoff_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    distance = models.FloatField()
    estimated_duration = models.DurationField()
    payment_method = models.CharField(max_length=50)
    user_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    driver_feedback = models.TextField(null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return f"Booking {self.id} by {self.user}"

    # Generate and assign OTP
    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()