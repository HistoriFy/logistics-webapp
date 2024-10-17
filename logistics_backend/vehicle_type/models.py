from django.db import models

class VehicleType(models.Model):
    vehicle_type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=100)
    description = models.TextField()
    capacity = models.FloatField()
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.type_name