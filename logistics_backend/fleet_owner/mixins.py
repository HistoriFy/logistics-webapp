from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from utils.exceptions import BadRequest, Unauthorized

from authentication.models import Driver
from fleet_owner.models import Vehicle

class VehicleAssignmentMixin:
    def get_fleet_owner(self, request):
        return request.user

    def validate_driver_and_vehicle(self, fleet_owner, driver_id, vehicle_id):
        try:
            driver = Driver.objects.get(pk=driver_id)
            vehicle = Vehicle.objects.get(pk=vehicle_id)
            
            if driver.fleet_owner != fleet_owner:
                raise Unauthorized('Driver does not belong to you.')
            if vehicle.fleet_owner != fleet_owner:
                raise Unauthorized('Vehicle does not belong to you.')

            return driver, vehicle
        except Driver.DoesNotExist:
            raise BadRequest('Driver does not exist.')
        except Vehicle.DoesNotExist:
            raise BadRequest('Vehicle does not exist.')

    def send_vehicle_assignment_update(self, driver, vehicle, status):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"driver_{driver.id}_available_bookings",
            {
                'type': 'vehicle_assignment_update',
                'message': {
                    'status': status,
                    'vehicle_id': vehicle.vehicle_id,
                    'license_plate': vehicle.license_plate,
                    'vehicle_type': vehicle.vehicle_type.type_name,
                    'capacity': vehicle.capacity,
                    'make': vehicle.make,
                    'model': vehicle.model,
                    'year': vehicle.year,
                    'color': vehicle.color,
                }
            }
        )