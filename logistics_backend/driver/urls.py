from django.urls import path

from .views import (AcceptBookingView,
                   RejectBookingView,
                   ToggleDriverAvailabilityView,
                   ValidateOTPView,
                   DriverCancelBookingView,
                   DriverCompleteRideView,
                   DriverSimulateToggleView,
                   FetchAllPastBookingsView)
                   

urlpatterns = [
    path('toggle-availability/', ToggleDriverAvailabilityView.as_view(), name='toggle-availability'),
    path('accept-booking/', AcceptBookingView.as_view(), name='accept-booking'),
    path('reject-booking/', RejectBookingView.as_view(), name='reject-booking'),
    path('validate-otp/', ValidateOTPView.as_view(), name='validate-otp'),
    path('bookings/cancel/driver/', DriverCancelBookingView.as_view(), name='cancel-booking-driver'),
    path('bookings/complete/driver/', DriverCompleteRideView.as_view(), name='complete-ride-driver'),
    path('simulate/toggle/', DriverSimulateToggleView.as_view(), name='simulate-toggle'),
    path('bookings/past/', FetchAllPastBookingsView.as_view(), name='fetch-past-bookings'),
]