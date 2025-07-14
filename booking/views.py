from typing import Any, cast

from django.db.models.query import QuerySet
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from user.models import CustomUser

from .models import Booking
from .serializers import BookingSerializer


class BookingView(ListAPIView, CreateAPIView):
    """
    List all bookings related to a customer or create Bookings
    """

    serializer_class = BookingSerializer

    def get_queryset(self) -> QuerySet[Booking]:
        user: CustomUser = cast(
            CustomUser,
            self.request.user,
        )
        queryset = Booking.objects.filter(customer__user=user).order_by("-created_at")
        return queryset

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """List all bookings related to a customer"""

        self.permission_classes = [IsAuthenticated]
        self.check_permissions(self.request)
        return self.list(request, *args, **kwargs)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Create a new booking and send a confirmation email.
        Automatically create the user if none associated to the email.
        Automatically create/update a customer with payload infos.
        """
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer: BaseSerializer) -> None:
        booking: Booking = serializer.save()
        booking.send_confirmation_email()
