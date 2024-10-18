from django.urls import path
from .views import UserBookingListView, UserCancelBookingView, UserCompleteRideView, UserFeedbackView

urlpatterns = [
    path("bookings/", UserBookingListView.as_view(), name="user-bookings"),
    path("bookings/cancel/user/", UserCancelBookingView.as_view(), name="cancel-booking-user"),
    path("bookings/complete/user/", UserCompleteRideView.as_view(), name="complete-ride-user"),
    path("bookings/feedback/", UserFeedbackView.as_view(), name="user-feedback"),
]
