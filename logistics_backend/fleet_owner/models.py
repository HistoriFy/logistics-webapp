from django.db import models

from authentication.models import Driver, FleetOwner
from vehicle_type.models import VehicleType

class Vehicle(models.Model):
    """
    Vehicle Model
    Attributes:
        vehicle_id (AutoField): Primary key for the vehicle.
        vehicle_type (ForeignKey): Foreign key to the VehicleType model.
        license_plate (CharField): Unique license plate number of the vehicle.
        capacity (FloatField): Capacity of the vehicle.
        make (CharField): Manufacturer of the vehicle.
        model (CharField): Model of the vehicle.
        year (IntegerField): Year the vehicle was manufactured.
        color (CharField): Color of the vehicle.
        driver (OneToOneField): One-to-one relationship with the Driver model. Can be null or blank.
        fleet_owner (ForeignKey): Foreign key to the FleetOwner model.
    Methods:
        __str__(): Returns the license plate of the vehicle as its string representation.
    """
    vehicle_id = models.AutoField(primary_key=True)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    license_plate = models.CharField(max_length=20, unique=True)
    capacity = models.FloatField()
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    color = models.CharField(max_length=50)
    driver = models.OneToOneField(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    fleet_owner = models.ForeignKey(FleetOwner, on_delete=models.CASCADE)

    def __str__(self):
        return self.license_plate
