from django.urls import path
from .views import AcceptBookingView, RejectBookingView, ToggleDriverAvailabilityView, ValidateOTPView

urlpatterns = [
    path('toggle-availability/', ToggleDriverAvailabilityView.as_view(), name='toggle-availability'),
    path('accept-booking/', AcceptBookingView.as_view(), name='accept-booking'),
    path('reject-booking/', RejectBookingView.as_view(), name='reject-booking'),
    path('validate-otp/', ValidateOTPView.as_view(), name='validate-otp'),
]