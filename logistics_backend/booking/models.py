from django.db import models
import random

from vehicle_type.models import VehicleType
from pricing_model.models import PricingModel

class Location(models.Model):
    """
    Location model representing a geographical location for pickup or dropoff.
    Attributes:
        PICKUP (str): Constant for pickup location type.
        DROPOFF (str): Constant for dropoff location type.
        LOCATION_TYPE_CHOICES (list): List of tuples representing location type choices.
        address (CharField): The address of the location.
        latitude (DecimalField): The latitude of the location with up to 9 digits and 7 decimal places.
        longitude (DecimalField): The longitude of the location with up to 9 digits and 7 decimal places.
        place_name (CharField): The name of the place.
        location_type (CharField): The type of location, either 'pickup' or 'dropoff'.
    """
    PICKUP = "pickup"
    DROPOFF = "dropoff"
    LOCATION_TYPE_CHOICES = [
        (PICKUP, "Pickup"),
        (DROPOFF, "Dropoff"),
    ]

    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=7)
    longitude = models.DecimalField(max_digits=9, decimal_places=7)
    place_name = models.CharField(max_length=255)
    location_type = models.CharField(max_length=10, choices=LOCATION_TYPE_CHOICES)

    def __str__(self):
        return f"{self.place_name} ({self.address})"

class Booking(models.Model):
    """
    Booking Model
    This model represents a booking in the logistics backend system. It contains information about the user, driver, vehicle type, locations, pricing, times, status, costs, distance, duration, payment method, rating, feedback, and OTP.
    Attributes:
        STATUS_CHOICES (list): List of possible status choices for a booking.
        user (ForeignKey): Reference to the user who made the booking.
        driver (ForeignKey): Reference to the driver assigned to the booking.
        vehicle_type (ForeignKey): Reference to the type of vehicle used for the booking.
        pickup_location (ForeignKey): Reference to the pickup location for the booking.
        dropoff_location (ForeignKey): Reference to the dropoff location for the booking.
        pricing (ForeignKey): Reference to the pricing model used for the booking.
        booking_time (DateTimeField): Timestamp when the booking was created.
        scheduled_time (DateTimeField): Scheduled time for the booking.
        pickup_time (DateTimeField): Actual pickup time for the booking.
        dropoff_time (DateTimeField): Actual dropoff time for the booking.
        status (CharField): Current status of the booking.
        estimated_cost (DecimalField): Estimated cost of the booking.
        actual_cost (DecimalField): Actual cost of the booking.
        distance (FloatField): Distance covered in the booking.
        estimated_duration (DurationField): Estimated duration of the booking.
        payment_method (CharField): Payment method used for the booking.
        rating (PositiveSmallIntegerField): Rating given to the booking.
        feedback (TextField): Feedback provided for the booking.
        otp (CharField): One-time password for starting the trip.
    """
    
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("on_trip", "On Trip"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("expired", "Expired"),
    ]

    user = models.ForeignKey("authentication.User", on_delete=models.CASCADE)
    driver = models.ForeignKey("authentication.Driver", on_delete=models.SET_NULL, null=True, blank=True)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    pickup_location = models.ForeignKey(Location, related_name="pickup_bookings", on_delete=models.CASCADE)
    dropoff_location = models.ForeignKey(Location, related_name="dropoff_bookings", on_delete=models.CASCADE)
    pricing = models.ForeignKey(PricingModel, on_delete=models.SET_NULL, null=True, blank=True)
    booking_time = models.DateTimeField(auto_now_add=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    pickup_time = models.DateTimeField(null=True, blank=True)
    dropoff_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    distance = models.FloatField()
    estimated_duration = models.DurationField()
    payment_method = models.CharField(max_length=50)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return f"Booking {self.id} by {self.user}"

    # Generate and assign OTP
    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()
