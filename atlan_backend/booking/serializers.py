from rest_framework import serializers

from .models import Booking, Location
from vehicle_type.models import VehicleType


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    pickup_location = LocationSerializer()
    dropoff_location = LocationSerializer()

    class Meta:
        model = Booking
        fields = '__all__'

class PlacePredictionSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=255)
    
class PriceEstimationSerializer(serializers.Serializer):
    origin_place_id = serializers.CharField(max_length=255)
    destination_place_id = serializers.CharField(max_length=255)
    place_type = serializers.ChoiceField(
        choices=[('city', 'City'), ('town', 'Town'), ('village', 'Village')],
        required=False
    )

class BookingCreateSerializer(serializers.Serializer):
    vehicle_type_id = serializers.IntegerField()
    pickup_address = serializers.CharField(max_length=255)
    pickup_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    pickup_place_name = serializers.CharField(max_length=255)
    dropoff_address = serializers.CharField(max_length=255)
    dropoff_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    dropoff_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    dropoff_place_name = serializers.CharField(max_length=255)
    scheduled_time = serializers.DateTimeField(required=False)
    payment_method = serializers.CharField(max_length=50)

    def validate_vehicle_type_id(self, value):
        if not VehicleType.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid vehicle type.")
        return value

    def validate(self, data):
        # Ensure pickup and dropoff locations are not the same
        if (data['pickup_latitude'] == data['dropoff_latitude'] and
                data['pickup_longitude'] == data['dropoff_longitude']):
            raise serializers.ValidationError("Pickup and dropoff locations cannot be the same.")
        return data