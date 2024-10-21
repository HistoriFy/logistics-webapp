from django.db import transaction
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from utils.custom_jwt_auth import CustomJWTAuthentication, IsRegularUser

from utils.helpers import format_response
from utils.exceptions import BadRequest, Unauthorized
from utils.google_endpoints import PlaceRepository

from booking.models import Booking
from booking.serializers import BookingSerializer

from driver.models import SimulationStatus

from .serializers import BookingUserCancelSerializer, UserFeedbackSerializer

class UserBookingListView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsRegularUser]

    @format_response
    def get(self, request):
        user = request.user
        bookings = Booking.objects.filter(user=user).order_by("-booking_time")
        serializer = BookingSerializer(bookings, many=True)

        response_data = {
            "user_id": user.id,
            "bookings": serializer.data
        }

        return (response_data, 200)

class UserCancelBookingView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsRegularUser]

    @format_response
    @transaction.atomic
    def post(self, request):
        user = request.user
        serializer = BookingUserCancelSerializer(data=request.data)

        if not serializer.is_valid():
            raise BadRequest(str(serializer.errors))

        booking_id = serializer.validated_data["booking_id"]
        feedback = serializer.validated_data["feedback"]

        try:
            booking = Booking.objects.select_for_update().get(id=booking_id)
            driver = booking.driver

            if booking.status not in ["pending", "accepted", "on_trip", "scheduled"]:
                raise BadRequest("Only bookings that are scheduled, pending, accepted or in-progress can be cancelled.")

            if booking.user != user:
                raise Unauthorized("You are not authorized to cancel this booking.")

            if booking.status != "pending":
                driver.status = "available"
                if SimulationStatus.objects.first().simulation_status:
                    driver.current_latitude = None
                    driver.current_longitude = None
                driver.save()

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"driver_{driver.id}_available_bookings",
                    {
                        "type": "available_booking_update",
                        "message": {
                            "status": "cancelled_by_user",
                            "booking_id": booking.id,
                            "pickup_location": booking.pickup_location.address,
                            "dropoff_location": booking.dropoff_location.address,
                        }
                    }
                )

            booking.status = "cancelled"
            booking.feedback = feedback
            booking.save()


            return ({"message": "Booking cancelled successfully."}, 200)

        except Booking.DoesNotExist:
            raise BadRequest("Booking does not exist.")

class UserCompleteRideView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsRegularUser]

    @format_response
    @transaction.atomic
    def post(self, request):
        user = request.user
        booking_id = request.data.get("booking_id")

        if not booking_id:
            raise BadRequest("Booking ID is required.")

        try:
            booking = Booking.objects.select_for_update().get(id=booking_id)

            if booking.status != "on_trip":
                raise BadRequest("Only trips that are in-progress can be completed.")

            if booking.user != user:
                raise Unauthorized("You are not authorized to complete this booking.")

            driver = booking.driver

            if not driver:
                raise BadRequest("No driver associated with this booking.")

            current_latitude = driver.current_latitude
            current_longitude = driver.current_longitude

            if not current_latitude or not current_longitude:
                raise BadRequest("Driver location is not available.")

            place_repository = PlaceRepository(api_key=settings.GOOGLE_API_KEY)
            distance_value, _ = place_repository.get_distance_and_time(
                origin_lat=current_latitude,
                origin_lng=current_longitude,
                destination_lat=booking.dropoff_location.latitude,
                destination_lng=booking.dropoff_location.longitude
            )

            if distance_value > 50:
                raise BadRequest("You must be within 50 meters of the dropoff location to complete the ride.")

            booking.status = "completed"
            booking.dropoff_time = timezone.now()
            booking.save()

            driver.status = "available"
            driver.total_rides += 1
            if SimulationStatus.objects.first().simulation_status:
                driver.current_latitude = None
                driver.current_longitude = None
                
            driver.save()

            return ({"message": "Ride completed successfully."}, 200)

        except Booking.DoesNotExist:
            raise BadRequest("Booking does not exist.")

class UserFeedbackView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsRegularUser]

    @format_response
    @transaction.atomic
    def post(self, request):
        serializer = UserFeedbackSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            booking_id = serializer.validated_data["booking_id"]
            rating = serializer.validated_data["rating"]
            feedback = serializer.validated_data.get("feedback", "")

            # Fetch the booking and driver
            booking = Booking.objects.get(id=booking_id)
            driver = booking.driver

            if not driver:
                raise BadRequest("No driver associated with this booking.")

            # Save feedback and rating on the booking
            booking.rating = rating
            booking.feedback = feedback
            booking.save()

            # Update the driver's rating and total rides
            total_rides = driver.total_rides
            current_avg_rating = driver.rating

            # Calculate the new average rating
            new_avg_rating = ((current_avg_rating * (total_rides - 1)) + rating) / total_rides
            driver.rating = new_avg_rating
            driver.save()

            return ({"message": "Feedback and rating submitted successfully."}, 201)

        return BadRequest(serializer.errors)
