from rest_framework import serializers

class BookingActionSerializer(serializers.Serializer):
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