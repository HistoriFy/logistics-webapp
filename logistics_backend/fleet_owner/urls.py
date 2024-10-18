from django.urls import path
from .views import (AddDriverView, AddVehicleView, AssignVehicleView,
                    DeassignVehicleView, ViewDriversView, ViewVehiclesView,
                    ViewVehiclesByDriverView, UpdateDriverView, UpdateVehicleView,
                    DeleteDriverView, DeleteVehicleView)

urlpatterns = [
    path('add_driver/', AddDriverView.as_view(), name='add_driver'),
    path('add_vehicle/', AddVehicleView.as_view(), name='add_vehicle'),
    path('assign_vehicle/', AssignVehicleView.as_view(), name='assign_vehicle'),
    path('deassign_vehicle/', DeassignVehicleView.as_view(), name='deassign_vehicle'),
    path('view_drivers/', ViewDriversView.as_view(), name='view_drivers'),
    path('view_vehicles/', ViewVehiclesView.as_view(), name='view_vehicles'),
    path('view_vehicles_by_driver/', ViewVehiclesByDriverView.as_view(), name='view_vehicles_by_driver'),
    path('update_driver/', UpdateDriverView.as_view(), name='update_driver'),
    path('update_vehicle/', UpdateVehicleView.as_view(), name='update_vehicle'),
    path('delete_driver/', DeleteDriverView.as_view(), name='delete_driver'),
    path('delete_vehicle/', DeleteVehicleView.as_view(), name='delete_vehicle'),
]
