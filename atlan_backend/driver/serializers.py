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

class ValidateOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6, min_length=6)
    booking_id = serializers.CharField(required=True)

    def validate_otp(self, value):
        if not value:
            raise serializers.ValidationError('OTP is required.')
        
        if isinstance(value, int):
            value = str(value)
            
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError('OTP must be a 6-digit number.')
        
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