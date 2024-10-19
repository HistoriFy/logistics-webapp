from django.db import models

class VehicleType(models.Model):
    """
    VehicleType model represents different types of vehicles in the logistics backend.
    Currently there are four types: 2 Wheeler, 3 Wheeler, Pickup, 14ft Truck.
    Attributes:
        vehicle_type_id (AutoField): The primary key for the vehicle type.
        type_name (CharField): The name of the vehicle type.
        description (TextField): A detailed description of the vehicle type.
        capacity (FloatField): The capacity of the vehicle type.
        image_url (URLField): An optional URL to an image representing the vehicle type.
    """
    vehicle_type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=100)
    description = models.TextField()
    capacity = models.FloatField()
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.type_name
