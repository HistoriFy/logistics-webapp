from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/fleet_owner/', include('fleet_owner.urls')),
    path('api/v1/driver/', include('driver.urls')),
    path('api/v1/regular_user/', include('regular_user.urls')),
    path('api/v1/booking/', include('booking.urls')),
    path('api/v1/vehicle_type/', include('vehicle_type.urls')),
]
