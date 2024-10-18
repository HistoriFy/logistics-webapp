from django.urls import path
from .views import GetVehicleTypeNamesView, GetAllVehicleTypeDetailsView

urlpatterns = [
    path("get_names/", GetVehicleTypeNamesView.as_view(), name="get_vehicle_type_names"),
    path("get_all_details/", GetAllVehicleTypeDetailsView.as_view(), name="get_all_vehicle_type_details"),
]
