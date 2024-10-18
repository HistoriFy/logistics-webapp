from rest_framework import serializers
from .models import User, Driver, FleetOwner

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=[("user", "User"), ("driver", "Driver"), ("fleet_owner", "FleetOwner")])

class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=[("user", "User"), ("driver", "Driver"), ("fleet_owner", "FleetOwner")])
    license_number = serializers.CharField(max_length=255, required=False)
    company_name = serializers.CharField(max_length=255, required=False)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists() or Driver.objects.filter(email=value).exists() or FleetOwner.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists() or Driver.objects.filter(phone=value).exists() or FleetOwner.objects.filter(phone=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def validate(self, data):
        user_type = data.get("user_type")
        if user_type == "driver" and not data.get("license_number"):
            raise serializers.ValidationError({"license_number": "This field is required for drivers."})
        if user_type == "fleet_owner" and not data.get("company_name"):
            raise serializers.ValidationError({"company_name": "This field is required for fleet owners."})
        return data
