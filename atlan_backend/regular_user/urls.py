# regular_user/urls.py

from django.urls import path
from .views import UserBookingListView

urlpatterns = [
    path('bookings/', UserBookingListView.as_view(), name='user-bookings'),
]