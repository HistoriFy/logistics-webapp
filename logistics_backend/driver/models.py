from django.db import models

class GPSTracking(models.Model):
    tracking_id = models.AutoField(primary_key=True)
    driver = models.ForeignKey("authentication.Driver", on_delete=models.CASCADE)
    booking = models.ForeignKey("booking.Booking", on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7)
    longitude = models.DecimalField(max_digits=9, decimal_places=7)
    speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    heading = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

class SimulationStatus(models.Model):
    simulation_status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.simulation_status)
