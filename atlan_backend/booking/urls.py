from django.urls import path
from .views import BookingCreateView, PlacePredictionView

urlpatterns = [
    path('create-booking/', BookingCreateView.as_view(), name='booking-create'),
    path('place-predictions/', PlacePredictionView.as_view(), name='place-predictions'),
]