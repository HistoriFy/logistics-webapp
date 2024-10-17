from django.utils import timezone
from rest_framework.views import APIView
from django.db import transaction
from django.conf import settings

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import GPSTracking
from authentication.models import Driver
from booking.models import Booking

from utils.custom_jwt_auth import CustomJWTAuthentication, IsDriver

from utils.helpers import format_response
from utils.exceptions import BadRequest, Unauthorized
from utils.google_endpoints import PlaceRepository

from .serializers import BookingActionSerializer, ValidateOTPSerializer, BookingDriverCancelSerializer, GPSTrackingSerializer

class GPSTrackingCreateView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsDriver]

    @format_response
    @transaction.atomic
    def post(self, request):
        serializer = GPSTrackingSerializer(data=request.data)
        
        if not serializer.is_valid():
            raise BadRequest(serializer.errors)
        
        driver = request.user
        
        booking = Booking.objects.filter(driver=driver, status__in=['on_trip', 'accepted']).first()
        booking_id = booking.id if booking else None
        
        gps_tracking = GPSTracking.objects.create(
            driver=driver,
            booking=booking,
            latitude=serializer.validated_data.get('latitude'),
            longitude=serializer.validated_data.get('longitude'),
            speed=serializer.validated_data.get('speed', None),
            heading=serializer.validated_data.get('heading', None),
        )
        
        driver.current_latitude = gps_tracking.latitude
        driver.current_longitude = gps_tracking.longitude
        driver.save()
        
        return ({
            'message': 'GPS data logged successfully.',
        }, 201)     

class AcceptBookingView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsDriver]

    @format_response
    @transaction.atomic
    def post(self, request):
        serializer = BookingActionSerializer(data=request.data)
        if not serializer.is_valid():
            raise BadRequest(serializer.errors)
        
        booking_id = serializer.validated_data['booking_id']  # Retrieve validated booking_id

        try:
            booking = Booking.objects.select_for_update().get(id=booking_id)

            if booking.status != 'pending':
                raise BadRequest('Booking is not available for acceptance.')

            driver = request.user

            if not driver.available_bookings.filter(id=booking_id).exists():
                raise Unauthorized('You are not authorized to accept this booking.')

            booking.driver = driver
            booking.status = 'accepted'
            booking.save()
            
            driver.status = 'on_trip'
            driver.save()
            
            booking.generate_otp()

            # Notify the user via WebSocket with the OTP
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{booking.user.id}_bookings",
                {
                    'type': 'send_otp_update',
                    'otp': booking.otp,
                    'booking_id': booking.id
                }
            )
            
            #Update the driver's available bookings
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"driver_{driver.id}_available_bookings",
                {
                    'type': 'available_booking_update',
                    'message': {
                        'status': 'accepted',
                        'booking_id': booking.id,
                        'pickup_location': booking.pickup_location.address,
                        'phone_number': booking.user.phone,
                        'dropoff_location': booking.dropoff_location.address,
                    }
                }
            )

            # Driver.objects.filter(available_bookings=booking).update(available_bookings=None)
            
            for driver in Driver.objects.filter(available_bookings=booking):
                driver.available_bookings.remove(booking)

            return ({'message': 'Booking accepted successfully.'}, 200)
        
        except Booking.DoesNotExist:
            raise BadRequest('Booking does not exist.')

class RejectBookingView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsDriver]

    @format_response
    @transaction.atomic
    def post(self, request):
        serializer = BookingActionSerializer(data=request.data)
        if not serializer.is_valid():
            raise BadRequest(serializer.errors)

        booking_id = serializer.validated_data['booking_id']

        try:
            booking = Booking.objects.get(id=booking_id)
            driver = request.user

            driver.available_bookings.remove(booking)

            return ({'message': 'Booking rejected successfully.'}, 200)
        except Booking.DoesNotExist:
            raise BadRequest('Booking does not exist.')

class DriverCancelBookingView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsDriver]

    @format_response
    @transaction.atomic
    def post(self, request):
        driver = request.user        
        serializer = BookingDriverCancelSerializer(data=request.data)
        
        if not serializer.is_valid():
            raise BadRequest(str(serializer.errors))
        
        booking_id = serializer.validated_data['booking_id']
        feedback = serializer.validated_data['feedback']

        try:
            booking = Booking.objects.select_for_update().get(id=booking_id)

            if booking.status not in ['accepted', 'on_trip']:
                raise BadRequest('Only accepted or on-trip bookings can be cancelled.')

            if booking.user != driver:
                raise Unauthorized('You are not authorized to cancel this booking.')

            booking.status = 'cancelled'
            booking.feedback = feedback
            booking.save()
            
            driver.status = 'available'
            driver.save()

            return ({'message': 'Booking cancelled successfully.'}, 200)
        
        except Booking.DoesNotExist:
            raise BadRequest('Booking does not exist.')     

class ToggleDriverAvailabilityView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsDriver]

    @format_response
    @transaction.atomic
    def post(self, request):
        driver = request.user

        # Toggle availability status
        if driver.availability_status == True:
            driver.availability_status = False
        elif driver.availability_status == False:
            driver.availability_status = True
        else:
            raise BadRequest('Driver is currently on a trip and cannot change availability status.')

        driver.save()

        return ({
            'message': f'Driver availability status toggled to {driver.availability_status}.',
        }, 200)

class ValidateOTPView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsDriver]

    @format_response
    @transaction.atomic
    def post(self, request):
        serializer = ValidateOTPSerializer(data=request.data)
        
        if serializer.is_valid():
            otp = serializer.validated_data['otp']
            booking_id = serializer.validated_data['booking_id'] 
            
            try:
                booking = Booking.objects.select_for_update().get(id=booking_id)

                if booking.status != 'accepted':
                    raise BadRequest('Booking is not in a valid state to start the trip.')

                if booking.otp != otp:
                    raise BadRequest('Invalid OTP.')

                booking.status = 'on_trip'
                booking.pickup_time = timezone.now()
                booking.save()
                
                # Send WebSocket update to the user about the trip starting
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"user_{booking.user.id}_bookings",
                    {
                        'type': 'booking_status_update',
                        'message': {
                            'status': 'on_trip',
                            'booking_id': booking.id,
                            'pickup_time': str(booking.pickup_time),
                            'message': 'OTP Verified. Trip has started.'
                        }
                    }
                )
                
                # Send WebSocket update to the driver about the trip starting
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"driver_{booking.driver.id}_available_bookings",
                    {
                        'type': 'available_booking_update',
                        'message': {
                            'status': 'on_trip',
                            'booking_id': booking.id,
                            'pickup_time': str(booking.pickup_time),
                        }
                    }
                )

                return ({'message': 'OTP validated. Booking status updated to on_trip.'}, 200)
            
            except Booking.DoesNotExist:
                raise BadRequest('Booking does not exist.')
        else:
            raise BadRequest(serializer.errors)

class DriverCompleteRideView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsDriver]

    @format_response
    @transaction.atomic
    def post(self, request):
        driver = request.user  # Authenticated driver
        booking_id = request.data.get('booking_id')  # Extract booking_id from request body

        if not booking_id:
            raise BadRequest('Booking ID is required.')

        try:
            booking = Booking.objects.select_for_update().get(id=booking_id)

            if booking.status != 'on_trip':
                raise BadRequest('Only trips that are in-progress can be completed.')

            if booking.driver != driver:
                raise Unauthorized('You are not authorized to complete this booking.')

            # Use the driver's current latitude and longitude from the Driver model
            current_latitude = driver.current_latitude
            current_longitude = driver.current_longitude

            if not current_latitude or not current_longitude:
                raise BadRequest('Driver location is not available.')

            # Use PlacesRepository to calculate the distance between current location and dropoff location
            place_repository = PlaceRepository(api_key=settings.GOOGLE_API_KEY)
            distance_value, _ = place_repository.get_distance_and_time(
                origin_lat=current_latitude,
                origin_lng=current_longitude,
                destination_lat=booking.dropoff_location.latitude,
                destination_lng=booking.dropoff_location.longitude
            )

            if distance_value > 50:
                raise BadRequest('You must be within 50 meters of the dropoff location to complete the ride.')

            # Mark the booking as completed
            booking.status = 'completed'
            booking.dropoff_time = timezone.now()  # Record the dropoff time
            booking.save()
            
            #Driver status update
            driver.status = 'available'
            driver.total_rides += 1
            driver.save()
            
            # Send WebSocket update to the driver about ride completion
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"driver_{driver.id}_available_bookings",
                {
                    'type': 'available_booking_update',
                    'message': {
                        'status': 'completed',
                        'booking_id': booking.id,
                        'dropoff_time': str(booking.dropoff_time),
                    }
                }
            )

            return ({'message': 'Ride completed successfully.'}, 200)
        
        except Booking.DoesNotExist:
            raise BadRequest('Booking does not exist.')