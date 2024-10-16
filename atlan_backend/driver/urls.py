from django.urls import path
from .views import AcceptBookingView, RejectBookingView

urlpatterns = [
    path('accept-booking/', AcceptBookingView.as_view(), name='accept-booking'),
    path('reject-booking/', RejectBookingView.as_view(), name='reject-booking'),
]