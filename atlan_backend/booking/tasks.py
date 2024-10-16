from celery import shared_task
from time import sleep
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Booking, Driver
from utils.google_endpoints import PlaceRepository

def notify_driver_about_booking(driver, booking):
    channel_layer = get_channel_layer()
    booking_data = {
        'booking_id': booking.id,
        'pickup_location': booking.pickup_location.address,
        'dropoff_location': booking.dropoff_location.address,
        'estimated_cost': float(booking.estimated_cost),
        'distance': booking.distance,
        'status': booking.status,
    }

    async_to_sync(channel_layer.group_send)(
        f"driver_{driver.id}_bookings",
        {
            "type": "booking_status_update",
            "message": booking_data,
        }
    )

@shared_task
def find_nearby_drivers(booking_id):
    booking = Booking.objects.get(id=booking_id)
    
    place_repository = PlaceRepository(api_key=settings.GOOGLE_API_KEY)
    search_radius = 1  # Initial radius in km
    time_elapsed = 0
    max_time = 300  # 5 minutes in seconds
    
    while time_elapsed <= max_time:
        available_drivers = Driver.objects.filter(availability_status='available')

        for driver in available_drivers:
            try:
                # Get distance between the booking's pickup location and the driver's current location
                distance_value, _ = place_repository.get_distance_and_time(
                    origin_lat=booking.pickup_location.latitude,
                    origin_lng=booking.pickup_location.longitude,
                    destination_lat=driver.current_latitude,
                    destination_lng=driver.current_longitude,
                    mode='driving'
                )

                distance_in_km = distance_value / 1000.0
                if distance_in_km <= search_radius:
                    # Add the booking to the driver's available bookings
                    driver.available_bookings.add(booking)

                    # Notify the driver about this booking (use WebSocket, FCM, etc.)
                    notify_driver_about_booking(driver, booking)

            except Exception as e:
                print(f"Error fetching distance: {str(e)}")

        search_radius += 1
        sleep(30)
        time_elapsed += 30

    # If no driver accepts the booking within 5 minutes, expire it
    booking.status = 'expired'
    booking.save()