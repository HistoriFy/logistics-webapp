from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction

from .models import User, Driver, FleetOwner
from .serializers import RegisterSerializer, LoginSerializer

from utils.custom_jwt_gen import generate_jwt_token
from utils.helpers import format_response
from utils.exceptions import BadRequest, Unauthorized


class RegisterView(APIView):

    @format_response
    @transaction.atomic
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            raise BadRequest(serializer.errors)

        user_type = serializer.validated_data["user_type"]
        email = serializer.validated_data["email"]
        phone = serializer.validated_data["phone"]
        name = serializer.validated_data["name"]
        password = make_password(serializer.validated_data["password"])

        if user_type == "user":
            user = User.objects.create(
                name=name,
                email=email,
                phone=phone,
                password=password
            )
            user_type = "User"

        elif user_type == "driver":
            license_number = serializer.validated_data["license_number"]
            user = Driver.objects.create(
                name=name,
                email=email,
                phone=phone,
                password=password,
                license_number=license_number
            )
            user_type = "Driver"

        elif user_type == "fleet_owner":
            company_name = serializer.validated_data["company_name"]
            user = FleetOwner.objects.create(
                name=name,
                email=email,
                phone=phone,
                password=password,
                company_name=company_name
            )
            user_type = "FleetOwner"

        else:
            raise BadRequest("Invalid user type.")

        token = generate_jwt_token(user, user_type.capitalize())

        return ({
            "token": token,
            "message": "Registration successful",
            "user_id": user.id
        }, 201)


class LoginView(APIView):

    @format_response
    @transaction.atomic
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            raise BadRequest(serializer.errors)

        user_type = serializer.validated_data["user_type"]
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        if user_type == "user":
            user = User.objects.filter(email=email).first()
            user_type = "User"

        elif user_type == "driver":
            user = Driver.objects.filter(email=email).first()
            user_type = "Driver"

        elif user_type == "fleet_owner":
            user = FleetOwner.objects.filter(email=email).first()
            user_type = "FleetOwner"

        else:
            raise BadRequest("Invalid user type.")

        if user and check_password(password, user.password):
            token = generate_jwt_token(user, user_type)

            return ({
                "token": token,
                "message": "Login successful"
            }, 200)

        else:
            raise Unauthorized("Invalid credentials.")
