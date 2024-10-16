from rest_framework.views import APIView
from rest_framework import status
from django.db import transaction

from authentication.models import Driver
from booking.models import Booking

from utils.helpers import validate_token, format_response
from utils.exceptions import BadRequest, Unauthorized
from .serializers import BookingActionSerializer

class AcceptBookingView(APIView):
    
    @validate_token(allowed_roles=['Driver'])
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
            
            driver.availability_status = 'on_trip'
            driver.save()

            Driver.objects.filter(available_bookings=booking).update(available_bookings=None)

            return ({'message': 'Booking accepted successfully.'}, 200)
        
        except Booking.DoesNotExist:
            raise BadRequest('Booking does not exist.')

class RejectBookingView(APIView):
    
    @validate_token(allowed_roles=['Driver'])
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
