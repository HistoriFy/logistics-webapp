from rest_framework import serializers

from booking.models import Booking

class BookingUserCancelSerializer(serializers.Serializer):
    booking_id = serializers.CharField(required=True)

    def validate_booking_id(self, value):
        if not value:
            raise serializers.ValidationError("Booking ID is required.")
        
        try:
            booking_id = int(value)
            if booking_id <= 0:
                raise serializers.ValidationError("Invalid booking ID.")
        except ValueError:
            raise serializers.ValidationError("Booking ID must be a valid integer.")
        
        return booking_id

class UserFeedbackSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    feedback = serializers.CharField(max_length=500, required=False)

    def validate_booking_id(self, value):
        user = self.context['request'].user

        try:
            booking = Booking.objects.get(id=value)
        except Booking.DoesNotExist:
            raise serializers.ValidationError('Booking does not exist.')

        if booking.user != user:
            raise serializers.ValidationError('You are not authorized to rate this booking.')

        if booking.status != 'completed':
            raise serializers.ValidationError('You can only rate a completed ride.')

        return value