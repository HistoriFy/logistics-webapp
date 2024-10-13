from rest_framework import serializers

from .models import Vehicle
from authentication.models import Driver
from vehicle_type.models import VehicleType

class DriverSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(max_length=255)
    license_number = serializers.CharField(max_length=50)

    def validate_email(self, value):
        if Driver.objects.filter(email=value).exists():
            raise serializers.ValidationError('Driver with this email already exists.')
        
        return value

    def validate_phone(self, value):
        if Driver.objects.filter(phone=value).exists():
            raise serializers.ValidationError('Driver with this phone number already exists.')
        
        return value

    def validate_license_number(self, value):
        if Driver.objects.filter(license_number=value).exists():
            raise serializers.ValidationError('Driver with this license number already exists.')
        
        return value

class VehicleSerializer(serializers.Serializer):
    vehicle_type_id = serializers.IntegerField()
    license_plate = serializers.CharField(max_length=20)
    capacity = serializers.FloatField()
    make = serializers.CharField(max_length=100)
    model = serializers.CharField(max_length=100)
    year = serializers.IntegerField()
    color = serializers.CharField(max_length=50)

    def validate_license_plate(self, value):
        if Vehicle.objects.filter(license_plate=value).exists():
            raise serializers.ValidationError('Vehicle with this license plate already exists.')
        
        return value

    def validate_vehicle_type_id(self, value):
        if not VehicleType.objects.filter(pk=value).exists():
            raise serializers.ValidationError('VehicleType with this ID does not exist.')
        
        return value

class AssignVehicleSerializer(serializers.Serializer):
    driver_id = serializers.IntegerField()
    vehicle_id = serializers.IntegerField()

    def validate(self, data):
        driver_id = data.get('driver_id')
        vehicle_id = data.get('vehicle_id')

        if not Driver.objects.filter(pk=driver_id).exists():
            raise serializers.ValidationError('Driver does not exist.')
        
        if not Vehicle.objects.filter(pk=vehicle_id).exists():
            raise serializers.ValidationError('Vehicle does not exist.')
        
        return data