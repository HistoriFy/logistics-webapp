from django.urls import path
from . import views

urlpatterns = [
    path('add_driver/', views.add_driver, name='add_driver'),
    path('add_vehicle/', views.add_vehicle, name='add_vehicle'),
    path('assign_vehicle/', views.assign_vehicle, name='assign_vehicle'),
    path('view_drivers/', views.view_drivers, name='view_drivers'),
    path('view_vehicles/', views.view_vehicles, name='view_vehicles'),
]
