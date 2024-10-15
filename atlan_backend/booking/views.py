from django.conf import Settings

from rest_framework.views import APIView
from decimal import Decimal
from datetime import timedelta

from .serializers import BookingCreateSerializer, PlacePredictionSerializer, PriceEstimationSerializer
from .models import Booking, Location

from vehicle_type.models import VehicleType
from pricing_model.models import PricingModel, Region

from utils.helpers import validate_token, format_response
from utils.exceptions import BadRequest
from utils.google_endpoints import PlaceRepository

class PlacePredictionView(APIView):
    
    @validate_token(allowed_roles=['User'])
    @format_response
    def get(self, request):
        serializer = PlacePredictionSerializer(data=request.query_params)
        if serializer.is_valid():
            query = serializer.validated_data['query']
            place_repository = PlaceRepository(api_key=Settings.GOOGLE_API_KEY)
            try:
                predictions = place_repository.get_places(query)
                return {'predictions': predictions}
            except Exception as e:
                raise BadRequest(str(e))
        else:
            raise BadRequest(serializer.errors)

class PriceEstimationView(APIView):
    
    @validate_token(allowed_roles=['User'])
    @format_response
    def post(self, request):
        serializer = PriceEstimationSerializer(data=request.data)
        if serializer.is_valid():
            origin_place_id = serializer.validated_data['origin_place_id']
            destination_place_id = serializer.validated_data['destination_place_id']
            place_type_input = serializer.validated_data.get('place_type')

            place_repository = PlaceRepository(api_key=Settings.GOOGLE_API_KEY)

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
                        'vehicle_type': vehicle_type.type_name,
                        'estimated_cost': float(round(estimated_cost, 2)),
                        'currency': 'INR'
                    })

                return {
                    'origin_place_type': origin_place_type,
                    'destination_place_type': destination_place_type,
                    'distance': round(distance_in_km, 2),
                    'estimated_duration_seconds': estimated_duration_seconds,
                    'price_estimations': price_estimations
                }

            except Exception as e:
                raise BadRequest(str(e))

        else:
            raise BadRequest(serializer.errors)

class BookingCreateView(APIView):
    
    @validate_token(allowed_roles=['User'])
    @format_response
    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            vehicle_type = VehicleType.objects.get(id=serializer.validated_data['vehicle_type_id'])

            pickup_location = Location.objects.create(
                address=serializer.validated_data['pickup_address'],
                latitude=serializer.validated_data['pickup_latitude'],
                longitude=serializer.validated_data['pickup_longitude'],
                place_name=serializer.validated_data['pickup_place_name'],
                location_type='pickup'
            )
            dropoff_location = Location.objects.create(
                address=serializer.validated_data['dropoff_address'],
                latitude=serializer.validated_data['dropoff_latitude'],
                longitude=serializer.validated_data['dropoff_longitude'],
                place_name=serializer.validated_data['dropoff_place_name'],
                location_type='dropoff'
            )

            place_repository = PlaceRepository(api_key=Settings.GOOGLE_API_KEY)

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

            pricing_model = PricingModel.objects.filter(vehicle_type=vehicle_type).first()
            if not pricing_model:
                raise BadRequest('Pricing model not found for the selected vehicle type')

            estimated_cost = (pricing_model.base_fare +
                              (pricing_model.per_km_rate * Decimal(distance_in_km)) +
                              (pricing_model.per_minute_rate * Decimal(estimated_duration_seconds / 60)))
            
            estimated_cost *= pricing_model.surge_multiplier

            booking = Booking.objects.create(
                user=user,
                vehicle_type=vehicle_type,
                pickup_location=pickup_location,
                dropoff_location=dropoff_location,
                status='pending',
                estimated_cost=estimated_cost,
                distance=distance_in_km,
                payment_method=serializer.validated_data['payment_method'],
                estimated_duration=estimated_duration,
                scheduled_time=serializer.validated_data.get('scheduled_time', None),
                pricing=pricing_model
            )

            response_data = {
                'booking_id': booking.id,
                'estimated_cost': float(booking.estimated_cost),
                'distance': booking.distance,
                'estimated_duration': estimated_duration_seconds,
                'status': booking.status
            }
            return response_data

        else:
            raise BadRequest(str(serializer.errors))