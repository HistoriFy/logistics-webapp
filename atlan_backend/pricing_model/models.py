from django.db import models

from vehicle_type.models import VehicleType

class Region(models.Model):
    region_id = models.AutoField(primary_key=True)
    region_name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.region_name


class PricingModel(models.Model):
    pricing_id = models.AutoField(primary_key=True)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, related_name='pricing_models')
    region = models.ForeignKey('Region', on_delete=models.CASCADE, related_name='pricing_models')
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    per_km_rate = models.DecimalField(max_digits=10, decimal_places=2)
    per_minute_rate = models.DecimalField(max_digits=10, decimal_places=2)
    surge_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    effective_start_date = models.DateField()
    effective_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle_type} - {self.region}"

class SurgePricing(models.Model):
    surge_pricing_id = models.AutoField(primary_key=True)
    region = models.ForeignKey('Region', on_delete=models.CASCADE, related_name='surge_pricings')
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, related_name='surge_pricings')
    surge_multiplier = models.DecimalField(max_digits=4, decimal_places=2)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.vehicle_type} - {self.region} ({self.start_time} - {self.end_time})"
