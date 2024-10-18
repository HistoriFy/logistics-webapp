from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Booking
from booking.serializers import BookingSerializer

@receiver(post_save, sender=Booking)
def send_booking_status_update(sender, instance, created, **kwargs):
    if not created:
        channel_layer = get_channel_layer()
        group_name = f"user_{instance.user.id}_bookings"

        serializer = BookingSerializer(instance)
        message = {
            "type": "booking_status_update",
            "message": serializer.data
        }

        async_to_sync(channel_layer.group_send)(
            group_name,
            message
        )
