from rest_framework.views import APIView

from .models import VehicleType

from utils.custom_jwt_auth import CustomJWTAuthentication
from utils.helpers import format_response

class GetVehicleTypeNamesView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    @format_response
    def get(self, request):

        vehicle_types = VehicleType.objects.all()
        vehicle_type_names = [vehicle_type.type_name for vehicle_type in vehicle_types]
        return ({"vehicle_type_names": vehicle_type_names}, 200)

class GetAllVehicleTypeDetailsView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    @format_response
    def get(self, request):

        vehicle_types = VehicleType.objects.all()

        vehicle_type_details = [
            {
                "vehicle_type_id": vehicle_type.vehicle_type_id,
                "type_name": vehicle_type.type_name,
                "description": vehicle_type.description,
                "capacity": vehicle_type.capacity,
                "image_url": vehicle_type.image_url,
            }
            for vehicle_type in vehicle_types
        ]

        return ({"vehicle_type_details": vehicle_type_details}, 200)
