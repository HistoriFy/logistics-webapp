from django.db import models

from vehicle_type.models import VehicleType

class Region(models.Model):
    """
    Geographical Regions for different surge pricing
    Namely Three: City, Town, Village
    
    Attributes:
        region_id (AutoField): The primary key for the region.
        region_name (CharField): The name of the region, must be unique and have a maximum length of 100 characters.
        description (TextField): A detailed description of the region.
    """
    
    region_id = models.AutoField(primary_key=True)
    region_name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.region_name


class PricingModel(models.Model):
    """
    Represents the Base pricing structure for different vehicle types and regions.
    Attributes:
        pricing_id (AutoField): The primary key for the pricing model.
        vehicle_type (ForeignKey): A foreign key to the VehicleType model, representing the type of vehicle.
        region (ForeignKey): A foreign key to the Region model, representing the region for which the pricing is applicable.
        base_fare (DecimalField): The base fare for the pricing model.
        per_km_rate (DecimalField): The rate charged per kilometer.
        per_minute_rate (DecimalField): The rate charged per minute.
        surge_multiplier (DecimalField): A multiplier applied during surge pricing, default is 1.0.
        effective_start_date (DateField): The date from which the pricing model becomes effective.
        effective_end_date (DateField, optional): The date until which the pricing model is effective, can be null or blank.
    """
    pricing_id = models.AutoField(primary_key=True)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, related_name="pricing_models")
    region = models.ForeignKey("Region", on_delete=models.CASCADE, related_name="pricing_models")
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    per_km_rate = models.DecimalField(max_digits=10, decimal_places=2)
    per_minute_rate = models.DecimalField(max_digits=10, decimal_places=2)
    surge_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    effective_start_date = models.DateField()
    effective_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle_type} - {self.region}"

class SurgePricing(models.Model):
    """
    Model representing surge pricing details for different regions and vehicle types.
    i.e. 2 Wheelers have more surge pricing in City than in Town.
    
    Attributes:
        surge_pricing_id (AutoField): Primary key for the SurgePricing model.
        region (ForeignKey): Foreign key to the Region model, representing the region where the surge pricing is applicable.
        vehicle_type (ForeignKey): Foreign key to the VehicleType model, representing the type of vehicle for which the surge pricing is applicable.
        surge_multiplier (DecimalField): Multiplier to be applied to the base price during surge pricing periods.
        start_time (TimeField): The start time of the surge pricing period.
        end_time (TimeField): The end time of the surge pricing period.
    """
    
    surge_pricing_id = models.AutoField(primary_key=True)
    region = models.ForeignKey("Region", on_delete=models.CASCADE, related_name="surge_pricings")
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, related_name="surge_pricings")
    surge_multiplier = models.DecimalField(max_digits=4, decimal_places=2)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.vehicle_type} - {self.region} ({self.start_time} - {self.end_time})"
