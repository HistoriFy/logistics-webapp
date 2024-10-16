from rest_framework.views import APIView

from utils.helpers import validate_token, format_response
from booking.models import Booking
from booking.serializers import BookingSerializer

class UserBookingListView(APIView):

    @validate_token(allowed_roles=['User'])
    @format_response
    def get(self, request):
        user = request.user
        bookings = Booking.objects.filter(user=user).order_by('-booking_time')
        serializer = BookingSerializer(bookings, many=True)
        
        response_data = {
            'user_id': user.id,
            'bookings': serializer.data
        }

        return (response_data, 200)
