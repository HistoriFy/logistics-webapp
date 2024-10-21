from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from authentication.models import Driver
from .models import Booking
from booking.serializers import BookingSerializer

# Signal to send live updates to the user when the status of their booking changes
@receiver(post_save, sender=Booking)
def send_booking_status_update(sender, instance, created, **kwargs):
    if not created:
        channel_layer = get_channel_layer()
        group_name = f"user_{instance.user.id}_bookings"
        
        serializer = BookingSerializer(instance)
        
        if instance.driver:
            driver_name = Driver.objects.get(id=instance.driver_id).name
            driver_rating = Driver.objects.get(id=instance.driver_id).rating
            driver_phone_number = Driver.objects.get(id=instance.driver_id).phone
            
            serializer.data["driver_phone_number"] = driver_phone_number
            serializer.data["driver_name"] = driver_name
            serializer.data["driver_rating"] = driver_rating

        serializer = BookingSerializer(instance)
        message = {
            "type": "booking_status_update",
            "message": serializer.data
        }

        async_to_sync(channel_layer.group_send)(
            group_name,
            message
        )
