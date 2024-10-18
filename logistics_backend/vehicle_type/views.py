from rest_framework.views import APIView

from .models import VehicleType

from utils.custom_jwt_auth import CustomJWTAuthentication, IsDriver, IsFleetOwner, IsRegularUser
from utils.helpers import format_response

class GetVehicleTypeNamesView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsDriver, IsFleetOwner, IsRegularUser]
    
    @format_response
    def get(self, request):
        
        vehicle_types = VehicleType.objects.all()
        vehicle_type_names = [vehicle_type.type_name for vehicle_type in vehicle_types]
        return ({'vehicle_type_names': vehicle_type_names}, 200)
