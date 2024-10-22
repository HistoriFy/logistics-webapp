from celery import shared_task
import after_response
from time import sleep
from django.conf import settings

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from vehicle_type.models import VehicleType
from authentication.models import Driver
from .models import Booking

from utils.google_endpoints import PlaceRepository
from driver.helpers import generate_random_location

def notify_driver_about_booking(driver, booking):
    channel_layer = get_channel_layer()
    
    vehicle_type = booking.vehicle_type
    
    vehicle_type_name = vehicle_type.type_name
    vehicle_type_url = vehicle_type.image_url
    vehicle_weight = vehicle_type.capacity
    vehicle_dimensions = vehicle_type.description
    
    booking_data = {
        "booking_id": booking.id,
        "pickup_location": booking.pickup_location.address,
        "dropoff_location": booking.dropoff_location.address,
        "estimated_cost": float(booking.estimated_cost),
        "distance": booking.distance,
        "vehicle_type_id": vehicle_type_name,
        "vehicle_type_url": vehicle_type_url,
        "vehicle_weight": vehicle_weight,
        "vehicle_dimensions": vehicle_dimensions,
        "status": booking.status,
    }

    async_to_sync(channel_layer.group_send)(
        f"driver_{driver.id}_bookings",
        {
            "type": "booking_status_update",
            "message": booking_data,
        }
    )

@shared_task
# @after_response.enable
def find_nearby_drivers(booking_id):
    # print("Celery task started")
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        print(f"Booking {booking_id} not found.")
        return

    place_repository = PlaceRepository(api_key=settings.GOOGLE_API_KEY)
    search_radius = settings.SEARCH_RADIUS

    time_elapsed = 0
    max_time = settings.MAX_SEARCH_TIME

    while time_elapsed <= max_time:
        booking.refresh_from_db()
        if booking.status in ["accepted", "on_trip"]:
            # print(f"Booking {booking.id} already accepted or in progress.")
            return

        available_drivers = Driver.objects.filter(status="available")
        found_driver = False

        for driver in available_drivers:
            try:
                if not driver.current_latitude and not driver.current_longitude:
                    driver.current_latitude, driver.current_longitude = generate_random_location(
                        booking.pickup_location.latitude, booking.pickup_location.longitude
                    )
                    driver.save()

                # print(f"Driver {driver.id} is at {driver.current_latitude}, {driver.current_longitude}")
                # print(f"Calling get_distance_and_time for booking {booking.id} and driver {driver.id}")
                # print(f"Pickup location: {booking.pickup_location.latitude}, {booking.pickup_location.longitude}")

                distance_value, _ = place_repository.get_distance_and_time(
                    origin_lat=booking.pickup_location.latitude,
                    origin_lng=booking.pickup_location.longitude,
                    destination_lat=driver.current_latitude,
                    destination_lng=driver.current_longitude,
                    mode="driving"
                )

                distance_in_km = distance_value / 1000.0
                if distance_in_km <= search_radius:
                    driver.available_bookings.add(booking)
                    notify_driver_about_booking(driver, booking)

                    if booking.status in ["accepted", "on_trip"]:
                        found_driver = True

            except Exception as e:
                print(f"Error fetching distance: {str(e)}")

        if found_driver:
            pass
        else:
            pass
            # print(f"No available drivers within {search_radius} km for booking {booking.id}.")

        if booking.status in ["accepted", "on_trip"]:
            break

        search_radius += 1
        sleep(30)
        time_elapsed += 30

    if booking.status not in ["accepted", "on_trip", "cancelled"]:
        booking.status = "expired"
        booking.save()
        # print(f"Booking {booking.id} expired after {max_time / 60} minutes.")



# async def find_nearby_drivers_async(booking_id):
#     # Wrap synchronous database calls with sync_to_async
#     booking = await sync_to_async(Booking.objects.get)(id=booking_id)
#     place_repository = PlaceRepository(api_key=settings.GOOGLE_API_KEY)

#     search_radius = 1  # Initial radius in km
#     time_elapsed = 0
#     max_time = 300  # 5 minutes in seconds

#     while time_elapsed <= max_time:
#         available_drivers = await sync_to_async(Driver.objects.filter)(status='available')

#         for driver in available_drivers:
#             try:
#                 # Use sync_to_async for external API calls if they are synchronous
#                 distance_value, _ = await sync_to_async(place_repository.get_distance_and_time)(
#                     origin_lat=booking.pickup_location.latitude,
#                     origin_lng=booking.pickup_location.longitude,
#                     destination_lat=driver.current_latitude,
#                     destination_lng=driver.current_longitude,
#                     mode='driving'
#                 )

#                 distance_in_km = distance_value / 1000.0
#                 if distance_in_km <= search_radius:
#                     # Update driver and booking relations
#                     await sync_to_async(driver.available_bookings.add)(booking)
#                     notify_driver_about_booking(driver, booking)
#             except Exception as e:
#                 print(f"Error fetching distance: {str(e)}")

#         search_radius += 1
#         await asyncio.sleep(30)
#         time_elapsed += 30

#     # Update booking status asynchronously
#     booking.status = 'expired'
#     await sync_to_async(booking.save)()
