from django.urls import path
from .views import  (BookingCreateView, PlacePredictionView,
                    PriceEstimationView, PlaceLatLongView,
                    LatLongPlaceTypeView)

urlpatterns = [
    path('create-booking/', BookingCreateView.as_view(), name='booking-create'),
    path('place-predictions/', PlacePredictionView.as_view(), name='place-predictions'),
    path('price-estimation/', PriceEstimationView.as_view(), name='price-estimation'),
    path('convert-place-id/', PlaceLatLongView.as_view(), name='convert-place-id'),
    path('convert-lat-long/', LatLongPlaceTypeView.as_view(), name='convert-lat-long'),
]