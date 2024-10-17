from time import sleep
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import after_response

from booking.models import Booking
from authentication.models import Driver
from .helpers import generate_random_location, move_towards

@after_response.enable
def simulate_driver_movement(booking_id):
    try:
        driver = Driver.objects.filter(status='available', availability_status=True).first()
        if not driver:
            print("No available driver found for Simulation. Restart the process...")
            return
        
        # Get the booking associated with this task
        booking = Booking.objects.get(id=booking_id)
        
        # Get the pickup and dropoff coordinates from the booking
        pickup_lat = float(booking.pickup_location.latitude)
        pickup_lng = float(booking.pickup_location.longitude)
        dropoff_lat = float(booking.dropoff_location.latitude)
        dropoff_lng = float(booking.dropoff_location.longitude)
        
        # Initialize control flags
        pending_handled = False
        accepted_handled = False
        near_pickup = False

        # Main movement loop, exit when booking is either completed or canceled or expired
        while booking.status not in ['completed', 'cancelled', 'expired']:
            booking.refresh_from_db()  # Ensure booking status is up-to-date
            
            # Simulate pending state (random location generation)
            if booking.status == 'pending' and not pending_handled:
                # print("Booking is pending. Generating random location near the pickup point for driver.")
                new_lat, new_lng = generate_random_location(pickup_lat, pickup_lng)
                driver.current_latitude = new_lat
                driver.current_longitude = new_lng
                driver.save()
                pending_handled = True
                # _broadcast_location_update(driver, booking, status="driver_found")
            
            # Simulate movement to pickup location after booking is accepted
            if booking.status == 'accepted' and not accepted_handled:
                # print("Booking is accepted. Moving driver towards pickup location...")
                new_lat, new_lng = move_towards(driver.current_latitude, driver.current_longitude, pickup_lat, pickup_lng)
                driver.current_latitude = new_lat
                driver.current_longitude = new_lng
                driver.save()
                _broadcast_location_update(driver, booking, status="en_route_to_pickup")

                # Check if driver is at the pickup location
                if (new_lat, new_lng) == (pickup_lat, pickup_lng):
                    _broadcast_location_update(driver, booking, status="at_pickup")
                    # print("Driver has reached the pickup location...")
                    accepted_handled = True
            
            # Simulate movement during the trip (on the way to dropoff location)
            if booking.status == 'on_trip':
                # print("Driver is on trip. Moving driver towards dropoff location...")
                new_lat, new_lng = move_towards(driver.current_latitude, driver.current_longitude, dropoff_lat, dropoff_lng)
                driver.current_latitude = new_lat
                driver.current_longitude = new_lng
                driver.save()
                _broadcast_location_update(driver, booking, status="on_trip")

                # If the driver reaches the dropoff location, broadcast that the driver is at the dropoff point
                if (new_lat, new_lng) == (dropoff_lat, dropoff_lng):
                    # print("Driver has reached the dropoff location...")
                    _broadcast_location_update(driver, booking, status="at_dropoff")
                    return  # End the simulation as the trip is completed
            
            sleep(5)  # Delay before next location update

    except Booking.DoesNotExist:
        print(f"Booking with ID {booking_id} does not exist. Restart the process...")


def _broadcast_location_update(driver, booking=None, status=None):
    """Helper function to broadcast the driver's updated location via WebSocket."""
    channel_layer = get_channel_layer()
    
    message_to_be_sent = {
        'type': 'location_update',
        'driver_id': driver.id,
        'current_latitude': driver.current_latitude,
        'current_longitude': driver.current_longitude,
        'status': status
    }
    
    async_to_sync(channel_layer.group_send)(
        f"user_{booking.user.id}_bookings",
        message_to_be_sent
    )