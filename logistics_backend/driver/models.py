from django.db import models

class GPSTracking(models.Model):
    """
    GPSTracking model to store GPS tracking data for drivers.
    Attributes:
        tracking_id (AutoField): Primary key for the GPS tracking record.
        driver (ForeignKey): Reference to the driver being tracked.
        booking (ForeignKey): Reference to the booking associated with the tracking, can be null or blank.
        timestamp (DateTimeField): Timestamp when the GPS data was recorded, automatically set on creation.
        latitude (DecimalField): Latitude coordinate of the GPS location.
        longitude (DecimalField): Longitude coordinate of the GPS location.
        speed (DecimalField): Speed of the vehicle at the time of recording, can be null or blank.
        heading (DecimalField): Heading direction of the vehicle at the time of recording, can be null or blank.
    """
    tracking_id = models.AutoField(primary_key=True)
    driver = models.ForeignKey("authentication.Driver", on_delete=models.CASCADE)
    booking = models.ForeignKey("booking.Booking", on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7)
    longitude = models.DecimalField(max_digits=9, decimal_places=7)
    speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    heading = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

class SimulationStatus(models.Model):
    """
    Model representing the status of the GPS simulation feature!
    Attributes:
        simulation_status (bool): A boolean field indicating the status of the simulation. 
                                  Defaults to False.
    """
    simulation_status = models.BooleanField(default=True)

    def __str__(self):
        return str(self.simulation_status)
