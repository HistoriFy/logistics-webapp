from django.utils import timezone
from datetime import datetime
from rest_framework import serializers

from .models import Booking, Location
from vehicle_type.models import VehicleType

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"

class BookingSerializer(serializers.ModelSerializer):
    pickup_location = LocationSerializer()
    dropoff_location = LocationSerializer()

    class Meta:
        model = Booking
        fields = "__all__"

class PlacePredictionSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=255)

class PriceEstimationSerializer(serializers.Serializer):
    origin_place_id = serializers.CharField(max_length=255)
    destination_place_id = serializers.CharField(max_length=255)
    place_type = serializers.ChoiceField(
        choices=[("city", "City"), ("town", "Town"), ("village", "Village")],
        required=False
    )

class PlaceLatLongSerializer(serializers.Serializer):
    place_id = serializers.CharField(max_length=255)

    def validate_place_id(self, value):
        if not value.strip():
            raise serializers.ValidationError("Place ID cannot be empty.")
        return value

class LatLongPlaceTypeSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=7)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=7)

    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value


class BookingCreateSerializer(serializers.Serializer):
    vehicle_type_id = serializers.IntegerField()
    pickup_address = serializers.CharField(max_length=255)
    pickup_latitude = serializers.DecimalField(max_digits=9, decimal_places=7)
    pickup_longitude = serializers.DecimalField(max_digits=9, decimal_places=7)
    dropoff_address = serializers.CharField(max_length=255)
    dropoff_latitude = serializers.DecimalField(max_digits=9, decimal_places=7)
    dropoff_longitude = serializers.DecimalField(max_digits=9, decimal_places=7)
    place_type = serializers.ChoiceField(
        choices=[("city", "City"), ("town", "Town"), ("village", "Village")],
        required=False
    )
    scheduled_time = serializers.DateTimeField(required=False)
    payment_method = serializers.CharField(max_length=50)

    def validate_vehicle_type_id(self, value):
        if not VehicleType.objects.filter(vehicle_type_id=value).exists():
            raise serializers.ValidationError("Invalid vehicle type.")
        return value
    
    def validate_scheduled_time(self, value):
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                raise serializers.ValidationError("Invalid format for scheduled_time. Use ISO 8601 format.")
        
        if not isinstance(value, datetime) or value.tzinfo is None:
            raise serializers.ValidationError("scheduled_time must be a timezone-aware datetime object.")
        
        if value.astimezone(timezone.utc) < timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future.")
        
        return value

    def validate(self, data):
        # Ensure pickup and dropoff locations are not the same
        if (data["pickup_latitude"] == data["dropoff_latitude"] and
                data["pickup_longitude"] == data["dropoff_longitude"]):
            raise serializers.ValidationError("Pickup and dropoff locations cannot be the same.")
        return data
