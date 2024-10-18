from django.db import transaction
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Vehicle
from .serializers import DriverSerializer, VehicleSerializer, AssignVehicleSerializer, DeassignVehicleSerializer
from .mixins import VehicleAssignmentMixin

from authentication.models import Driver, FleetOwner
from vehicle_type.models import VehicleType

from utils.custom_jwt_auth import CustomJWTAuthentication, IsFleetOwner

from utils.exceptions import Unauthorized, BadRequest
from utils.helpers import format_response


class AddDriverView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsFleetOwner]

    @format_response
    @transaction.atomic
    def post(self, request):
        try:
            fleet_owner = FleetOwner.objects.get(email=request.user.email)
            serializer = DriverSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            driver = Driver(
                email=serializer.validated_data['email'],
                name=serializer.validated_data['name'],
                phone=serializer.validated_data['phone'],
                password=make_password(serializer.validated_data['password']),
                license_number=serializer.validated_data['license_number'],
                fleet_owner=fleet_owner,
                availability_status=True
            )
            driver.save()

            return ({'message': 'Driver added successfully.'}, 201)

        except FleetOwner.DoesNotExist:
            raise Unauthorized('You are not authorized to perform this action.')
        except Exception as e:
            raise BadRequest(str(e))


class AddVehicleView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsFleetOwner]
    
    @format_response
    @transaction.atomic
    def post(self, request):
        try:
            fleet_owner = FleetOwner.objects.get(email=request.user.email)
            serializer = VehicleSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            vehicle_type = VehicleType.objects.get(pk=serializer.validated_data['vehicle_type_id'])

            vehicle = Vehicle(
                vehicle_type=vehicle_type,
                license_plate=serializer.validated_data['license_plate'],
                capacity=serializer.validated_data['capacity'],
                make=serializer.validated_data['make'],
                model=serializer.validated_data['model'],
                year=serializer.validated_data['year'],
                color=serializer.validated_data['color'],
                fleet_owner=fleet_owner
            )
            vehicle.save()

            return ({'message': 'Vehicle added successfully.'}, 201)

        except FleetOwner.DoesNotExist:
            raise Unauthorized('You are not authorized to perform this action.')
        except Exception as e:
            raise BadRequest(str(e))


class AssignVehicleView(APIView, VehicleAssignmentMixin):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsFleetOwner]

    @format_response
    @transaction.atomic
    def post(self, request):
        try:
            fleet_owner = self.get_fleet_owner(request)
            serializer = AssignVehicleSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            driver, vehicle = self.validate_driver_and_vehicle(
                fleet_owner, 
                serializer.validated_data['driver_id'], 
                serializer.validated_data['vehicle_id']
            )

            if vehicle.driver:
                raise BadRequest('Vehicle is already assigned to another driver.')
            if driver.status == 'on_trip':
                raise BadRequest('Driver is on trip. Cannot assign vehicle.')
            if not driver.availability_status:
                raise BadRequest('Driver is not available. Cannot assign vehicle.')

            self.send_vehicle_assignment_update(driver, vehicle, 'vehicle_assigned')

            vehicle.driver = driver
            vehicle.save()

            return {'message': 'Vehicle assigned to driver successfully.'}, 200

        except FleetOwner.DoesNotExist:
            raise Unauthorized('You are not authorized to perform this action.')
        except Exception as e:
            raise BadRequest(str(e))


class DeassignVehicleView(APIView, VehicleAssignmentMixin):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsFleetOwner]

    @format_response
    def post(self, request):
        serializer = DeassignVehicleSerializer(data=request.data)
        
        if serializer.is_valid():
            fleet_owner = self.get_fleet_owner(request)
            vehicle = serializer.validated_data['vehicle']
            driver = vehicle.driver

            if not driver:
                raise BadRequest('Vehicle is not assigned to any driver.')
            if driver.status == 'on_trip':
                raise BadRequest('Driver is on trip. Cannot de-assign vehicle.')
            if not driver.availability_status:
                raise BadRequest('Driver is not available. Cannot de-assign vehicle.')

            self.send_vehicle_assignment_update(driver, vehicle, 'vehicle_deassigned')

            vehicle.driver = None
            vehicle.save()

            return {'message': f'Driver {driver.id} has been de-assigned from vehicle {vehicle.vehicle_id}'}, 200
        else:
            raise BadRequest(serializer.errors)


class ViewDriversView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsFleetOwner]
    
    @format_response
    def get(self, request):
        try:
            fleet_owner = FleetOwner.objects.get(email=request.user.email)
            drivers = Driver.objects.filter(fleet_owner=fleet_owner)

            driver_list = [
                {
                    'driver_id': driver.id,
                    'name': driver.name,
                    'email': driver.email,
                    'phone': driver.phone,
                    'license_number': driver.license_number,
                    'status': driver.status,
                    'availability_status': driver.availability_status,
                }
                for driver in drivers
            ]

            return ({'drivers': driver_list}, 200)

        except FleetOwner.DoesNotExist:
            raise Unauthorized('You are not authorized to perform this action.')
        except Exception as e:
            raise BadRequest(str(e))


class ViewVehiclesView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsFleetOwner]
    
    @format_response
    def get(self, request):
        try:
            fleet_owner = FleetOwner.objects.get(email=request.user.email)
            vehicles = Vehicle.objects.filter(fleet_owner=fleet_owner)

            vehicle_list = [
                {
                    'vehicle_id': vehicle.vehicle_id,
                    'license_plate': vehicle.license_plate,
                    'vehicle_type': vehicle.vehicle_type.type_name,
                    'capacity': vehicle.capacity,
                    'make': vehicle.make,
                    'model': vehicle.model,
                    'year': vehicle.year,
                    'color': vehicle.color,
                    'driver': vehicle.driver.name if vehicle.driver else None
                }
                for vehicle in vehicles
            ]

            return ({'vehicles': vehicle_list}, 200)

        except FleetOwner.DoesNotExist:
            raise Unauthorized('You are not authorized to perform this action.')
        except Exception as e:
            raise BadRequest(str(e))

class ViewVehiclesByDriverView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsFleetOwner]

    @format_response
    def get(self, request):
        try:
            fleet_owner = FleetOwner.objects.get(email=request.user.email)
            drivers = Driver.objects.filter(fleet_owner=fleet_owner)
            vehicles = Vehicle.objects.filter(driver__in=drivers)

            if not vehicles.exists():
                return ({'message': 'No matched vehicles found for the fleet owner.'}, 200)

            vehicle_list = [
                {
                    'vehicle_id': vehicle.vehicle_id,
                    'license_plate': vehicle.license_plate,
                    'vehicle_type': vehicle.vehicle_type.type_name,
                    'driver_id': vehicle.driver.id,
                    'driver_name': vehicle.driver.name,
                    'driver_phone': vehicle.driver.phone,
                    'status': vehicle.driver.status,
                    'availability_status': vehicle.driver.availability_status,
                }
                for vehicle in vehicles
            ]

            return ({'vehicles': vehicle_list}, 200)

        except FleetOwner.DoesNotExist:
            raise Unauthorized('You are not authorized to perform this action.')
        except Exception as e:
            raise BadRequest(str(e))