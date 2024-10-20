from django.conf import settings
import asyncio
from rest_framework.views import APIView
from decimal import Decimal
from datetime import timedelta

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Booking, Location
from .serializers import (BookingCreateSerializer, PlacePredictionSerializer,
                         PriceEstimationSerializer, PlaceLatLongSerializer,
                         LatLongPlaceTypeSerializer, BookingSerializer)

from .tasks import find_nearby_drivers
from driver.tasks import simulate_driver_movement

from vehicle_type.models import VehicleType
from pricing_model.models import PricingModel, Region
from driver.models import SimulationStatus

from utils.custom_jwt_auth import CustomJWTAuthentication, IsRegularUser

from utils.helpers import format_response
from utils.exceptions import BadRequest
from utils.google_endpoints import PlaceRepository

class PlacePredictionView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsRegularUser]

    @format_response
    def get(self, request):
        serializer = PlacePredictionSerializer(data=request.query_params)
        if serializer.is_valid():
            query = serializer.validated_data["query"]
            place_repository = PlaceRepository(api_key=settings.GOOGLE_API_KEY)
            try:
                predictions = place_repository.get_places(query)
                return ({"predictions": predictions}, 200)
            except Exception as e:
                raise BadRequest(str(e))
        else:
            raise BadRequest(serializer.errors)


class PlaceLatLongView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsRegularUser]

    @format_response
    def post(self, request):
        serializer = PlaceLatLongSerializer(data=request.data)
        if serializer.is_valid():
            place_id = serializer.validated_data["place_id"]
            place_repository = PlaceRepository(api_key=settings.GOOGLE_API_KEY)

            try:
                lat, lng, place_type = place_repository.get_lat_lng_and_type_from_place_id(place_id)

                return ({
                    "latitude": lat,
                    "longitude": lng,
                    "place_type": place_type
                }, 200)

            except Exception as e:
                raise BadRequest(str(e))
        else:
            raise BadRequest(serializer.errors)

class LatLongPlaceTypeView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsRegularUser]

    @format_response
    def post(self, request):
        serializer = LatLongPlaceTypeSerializer(data=request.data)
        if serializer.is_valid():
            lat = serializer.validated_data["latitude"]
            lng = serializer.validated_data["longitude"]

            place_repository = PlaceRepository(api_key=settings.GOOGLE_API_KEY)

            try:
                place_id, location_name = place_repository.get_place_id_from_coordinates(lat, lng)

                return ({
                    "place_id": place_id,
                    "location_name": location_name
                }, 200)

            except Exception as e:
                raise BadRequest(str(e))

        else:
            raise BadRequest(serializer.errors)

class PriceEstimationView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsRegularUser]

    @format_response
    def post(self, request):
        serializer = PriceEstimationSerializer(data=request.data)
        if serializer.is_valid():
            origin_place_id = serializer.validated_data["origin_place_id"]
            destination_place_id = serializer.validated_data["destination_place_id"]
            place_type_input = serializer.validated_data.get("place_type")

            place_repository = PlaceRepository(api_key=settings.GOOGLE_API_KEY)

            try:
                origin_lat, origin_lng, origin_place_type = place_repository.get_lat_lng_and_type_from_place_id(origin_place_id)
                destination_lat, destination_lng, destination_place_type = place_repository.get_lat_lng_and_type_from_place_id(destination_place_id)

                if place_type_input:
                    origin_place_type = place_type_input.capitalize()
                    destination_place_type = place_type_input.capitalize()
                else:
                    origin_place_type = origin_place_type.capitalize()
                    destination_place_type = destination_place_type.capitalize()

                distance_value, estimated_duration_seconds = place_repository.get_distance_and_time(
                    origin_lat=origin_lat,
                    origin_lng=origin_lng,
                    destination_lat=destination_lat,
                    destination_lng=destination_lng
                )
                distance_in_km = distance_value / 1000.0
                estimated_duration_minutes = estimated_duration_seconds / 60.0

                region = Region.objects.filter(region_name=origin_place_type).first()
                if not region:
                    raise BadRequest(f"Region '{origin_place_type}' not found in the database")

                vehicle_types = VehicleType.objects.all()
                price_estimations = []

                for vehicle_type in vehicle_types:
                    pricing_model = PricingModel.objects.filter(vehicle_type=vehicle_type, region=region).first()
                    if not pricing_model:
                        continue

                    estimated_cost = (pricing_model.base_fare +
                                      (pricing_model.per_km_rate * Decimal(distance_in_km)) +
                                      (pricing_model.per_minute_rate * Decimal(estimated_duration_minutes)))
                    estimated_cost *= pricing_model.surge_multiplier

                    price_estimations.append({
                        "vehicle_type_id": vehicle_type.vehicle_type_id,
                        "vehicle_type": vehicle_type.type_name,
                        "vehicle_weight": vehicle_type.capacity,
                        "vehicle_dimensions": vehicle_type.description,
                        "vehicle_image_url": vehicle_type.image_url,
                        "estimated_cost": float(round(estimated_cost, 2)),
                        "currency": "INR"
                    })

                return ({
                    "origin_place_id": origin_place_id,
                    "origin_place_type": origin_place_type,
                    "origin_latitude": origin_lat,
                    "origin_longitude": origin_lng,
                    "destination_place_id": destination_place_id,
                    "destination_latitude": destination_lat,
                    "destination_longitude": destination_lng,
                    "destination_place_type": destination_place_type,
                    "distance": round(distance_in_km, 2),
                    "estimated_duration_seconds": estimated_duration_seconds,
                    "price_estimations": price_estimations
                }, 200)

            except Exception as e:
                raise BadRequest(str(e))

        else:
            raise BadRequest(serializer.errors)

class BookingCreateView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsRegularUser]
    
    def process_booking(self, serializer, booking, simulate_row):
        scheduled_time = serializer.validated_data.get("scheduled_time")
        
        ## find nearby drivers for the booking
        if scheduled_time:
            find_nearby_drivers.apply_async((booking.id,), eta=scheduled_time)
        else:
            find_nearby_drivers.delay(booking.id)
            
        ## simulate driver movement if simulation is enabled
        if simulate_row.simulation_status and scheduled_time:
            simulate_driver_movement.apply_async((booking.id,), eta=scheduled_time)
        elif simulate_row.simulation_status:
            simulate_driver_movement.delay(booking.id)

    @format_response
    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            try:
                vehicle_type = VehicleType.objects.get(vehicle_type_id=serializer.validated_data["vehicle_type_id"])
            except VehicleType.DoesNotExist:
                raise BadRequest("Invalid vehicle type ID")

            pickup_location = Location.objects.create(
                address=serializer.validated_data["pickup_address"],
                latitude=serializer.validated_data["pickup_latitude"],
                longitude=serializer.validated_data["pickup_longitude"],
                place_name=serializer.validated_data["pickup_address"],
                location_type="pickup"
            )
            dropoff_location = Location.objects.create(
                address=serializer.validated_data["dropoff_address"],
                latitude=serializer.validated_data["dropoff_latitude"],
                longitude=serializer.validated_data["dropoff_longitude"],
                place_name=serializer.validated_data["dropoff_address"],
                location_type="dropoff"
            )

            place_repository = PlaceRepository(api_key=settings.GOOGLE_API_KEY)

            try:
                distance_value, estimated_duration_seconds = place_repository.get_distance_and_time(
                    origin_lat=pickup_location.latitude,
                    origin_lng=pickup_location.longitude,
                    destination_lat=dropoff_location.latitude,
                    destination_lng=dropoff_location.longitude
                )
                distance_in_km = distance_value / 1000.0
                estimated_duration = timedelta(seconds=estimated_duration_seconds)
            except Exception as e:
                raise BadRequest(str(e))
            
            place_type = serializer.validated_data.get("place_type", "city")
            place_type = place_type.capitalize() if place_type else "City"

            try:
                pricing_model = PricingModel.objects.get(
                                    vehicle_type=vehicle_type, 
                                    region__region_name=place_type
                                )
            except PricingModel.DoesNotExist:
                raise BadRequest("Pricing model not found for the selected vehicle type")

            # costlier during afternoon in surge pricing. cheaper during night
            # costlier in cities, cheaper in rural areas
            estimated_cost = (pricing_model.base_fare +
                              (pricing_model.per_km_rate * Decimal(distance_in_km)) +
                              (pricing_model.per_minute_rate * Decimal(estimated_duration_seconds / 60)))
            estimated_cost *= pricing_model.surge_multiplier
            
            if serializer.validated_data.get("scheduled_time"):
                scheduled_time = serializer.validated_data["scheduled_time"]
                status = "scheduled"
            else:
                scheduled_time = None
                status = "pending"

            booking = Booking.objects.create(
                user=user,
                vehicle_type=vehicle_type,
                pickup_location=pickup_location,
                dropoff_location=dropoff_location,
                status=status,
                estimated_cost=estimated_cost,
                distance=distance_in_km,
                payment_method=serializer.validated_data["payment_method"],
                estimated_duration=estimated_duration,
                scheduled_time=scheduled_time,
                pricing=pricing_model
            )
            
            # update user about pending booking
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{booking.user.id}_bookings",
                {
                    "type": "booking_status_update",
                    "message": BookingSerializer(booking).data
                }
            )

            response_data = {
                "booking_id": booking.id,
                "estimated_cost": float(booking.estimated_cost),
                "scheduled_time": booking.scheduled_time,
                "distance": booking.distance,
                "estimated_duration": estimated_duration_seconds,
                "status": booking.status
            }
            
            simulate_row = SimulationStatus.objects.first()
            
            # process booking
            self.process_booking(serializer, booking, simulate_row)

            return (response_data, 201)

        else:
            raise BadRequest(serializer.errors)


class FetchAllPastBookingsView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsRegularUser]

    @format_response
    def get(self, request):
        user = request.user
        past_bookings = Booking.objects.filter(user=user, status__in=["completed", "cancelled", "expired", "scheduled"]).order_by("-booking_time")
        past_bookings_data = []

        for booking in past_bookings:
            past_bookings_data.append({
                "booking_id": booking.id,
                "vehicle_type": booking.vehicle_type.type_name if booking.vehicle_type else None,
                "pickup_address": booking.pickup_location.address,
                "dropoff_address": booking.dropoff_location.address,
                "status": booking.status,
                "estimated_cost": float(booking.estimated_cost),
                "distance": booking.distance,
                "scheduled_time": booking.scheduled_time,
                "payment_method": booking.payment_method,
                "created_at": booking.booking_time
            })

        return (past_bookings_data, 200)