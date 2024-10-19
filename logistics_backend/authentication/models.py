from django.db import models

class User(models.Model):
    """
    User model representing a user in the authentication system.

    Attributes:
        email (EmailField): The unique email address of the user.
        name (CharField): The name of the user, with a maximum length of 255 characters.
        phone (CharField): The unique phone number of the user, with a maximum length of 15 characters.
        password (CharField): The password of the user, stored as a hashed string with a maximum length of 255 characters.
        registration_date (DateTimeField): The date and time when the user registered, automatically set to the current date and time.
        status (BooleanField): The status of the user, indicating whether the user is active (default is True).
    """
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

class Driver(models.Model):
    """
    Driver Model
    Attributes:
        DRIVER_STATUS_CHOICES (list): Choices for the driver's status.
        email (EmailField): Unique email address of the driver.
        name (CharField): Name of the driver.
        phone (CharField): Unique phone number of the driver.
        password (CharField): Password for the driver's account.
        license_number (CharField): Unique license number of the driver.
        registration_date (DateTimeField): Date and time when the driver registered.
        status (CharField): Current status of the driver, with choices from DRIVER_STATUS_CHOICES.
        availability_status (BooleanField): Indicates if the driver is currently available.
        fleet_owner (ForeignKey): Reference to the FleetOwner, can be null or blank.
        available_bookings (ManyToManyField): Bookings that the driver is available for.
        total_rides (PositiveIntegerField): Total number of rides completed by the driver.
        rating (DecimalField): Rating of the driver, with a maximum of 3 digits and 2 decimal places.
        current_longitude (DecimalField): Current longitude of the driver, can be null or blank.
        current_latitude (DecimalField): Current latitude of the driver, can be null or blank.
    """
    
    DRIVER_STATUS_CHOICES = [
        ("available", "Available"),
        ("unavailable", "Unavailable"),
        ("on_trip", "On Trip")
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    license_number = models.CharField(max_length=50, unique=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="available", choices=DRIVER_STATUS_CHOICES)
    availability_status = models.BooleanField(default=True)
    fleet_owner = models.ForeignKey("FleetOwner", on_delete=models.CASCADE, null=True, blank=True)
    available_bookings = models.ManyToManyField("booking.Booking", related_name="available_drivers", blank=True)
    total_rides = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=7, null=True, blank=True)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=7, null=True, blank=True)

class FleetOwner(models.Model):
    """
    FleetOwner model represents a fleet owner in the logistics backend system.
    Attributes:
        email (EmailField): The unique email address of the fleet owner.
        name (CharField): The name of the fleet owner.
        phone (CharField): The unique phone number of the fleet owner.
        password (CharField): The password for the fleet owner's account.
        company_name (CharField): The name of the fleet owner's company.
        registration_date (DateTimeField): The date and time when the fleet owner registered, automatically set on creation.
    """
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    registration_date = models.DateTimeField(auto_now_add=True)
