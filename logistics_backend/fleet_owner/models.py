from django.db import models

from authentication.models import Driver, FleetOwner
from vehicle_type.models import VehicleType

class Vehicle(models.Model):
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
