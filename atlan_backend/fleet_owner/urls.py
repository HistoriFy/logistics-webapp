from django.urls import path
from .views import AddDriverView, AddVehicleView, AssignVehicleView, ViewDriversView, ViewVehiclesView

urlpatterns = [
    path('add_driver/', AddDriverView.as_view(), name='add_driver'),
    path('add_vehicle/', AddVehicleView.as_view(), name='add_vehicle'),
    path('assign_vehicle/', AssignVehicleView.as_view(), name='assign_vehicle'),
    path('view_drivers/', ViewDriversView.as_view(), name='view_drivers'),
    path('view_vehicles/', ViewVehiclesView.as_view(), name='view_vehicles'),
]
