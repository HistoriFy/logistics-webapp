from rest_framework import serializers

from authentication.models import Driver

class GPSTrackingSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=7)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=7)
    speed = serializers.FloatField(required=False, allow_null=True)
    heading = serializers.FloatField(required=False, allow_null=True)

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90 degrees.")
        return value

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180 degrees.")
        return value

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

class ValidateOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6, min_length=6)
    booking_id = serializers.CharField(required=True)

    def validate_otp(self, value):
        if not value:
            raise serializers.ValidationError("OTP is required.")

        if isinstance(value, int):
            value = str(value)

        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("OTP must be a 6-digit number.")

        return value

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

class BookingDriverCancelSerializer(serializers.Serializer):
    booking_id = serializers.CharField(required=True)
    feedback = serializers.CharField(required=True)

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

    def validate_feedback(self, value):
        if not value:
            raise serializers.ValidationError("Feedback is required.")

        return value
