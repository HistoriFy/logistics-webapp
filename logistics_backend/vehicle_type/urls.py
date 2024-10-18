from django.urls import path
from .views import GetVehicleTypeNamesView

urlpatterns = [
    path('get_names/', GetVehicleTypeNamesView.as_view(), name='get_vehicle_type_names'),
]
