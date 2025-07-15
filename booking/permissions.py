from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import Booking


class IsBookingOwner(IsAuthenticated):
    """
    Allow access only if authenticated user created the booking
    """

    def has_object_permission(
        self, request: Request, view: APIView, obj: Booking
    ) -> bool:
        return obj.customer.user == request.user
