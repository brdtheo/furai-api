from django.urls import path

from .views import BookingList

urlpatterns = [path("bookings", BookingList.as_view(), name="booking-list")]
