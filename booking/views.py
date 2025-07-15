from typing import Any, cast

from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import GenericViewSet

from user.models import CustomUser

from .enums import BookingStatus
from .errors import BOOKING_ALREADY_CANCELED_ERROR, BOOKING_CANCEL_COMPLETED_ERROR
from .models import Booking
from .permissions import IsBookingOwner
from .serializers import BookingSerializer


class BookingViewSet(CreateAPIView, ListAPIView, GenericViewSet):
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
        self.check_permissions(request)
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

    @action(detail=True, methods=["post"])
    def cancel(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Cancel a booking"""

        # Check permissions
        self.permission_classes = [IsBookingOwner]
        booking = get_object_or_404(Booking, pk=kwargs["pk"])
        self.check_object_permissions(request, booking)

        # Validation
        if booking.status == BookingStatus.COMPLETED:
            raise BOOKING_CANCEL_COMPLETED_ERROR
        if booking.status == (
            BookingStatus.CANCELED_BY_CUSTOMER or BookingStatus.CANCELED_BY_STAFF
        ):
            raise BOOKING_ALREADY_CANCELED_ERROR
        booking.cancel()

        # Send cancellation email
        if (
            booking.status is BookingStatus.CANCELED_BY_CUSTOMER
            or booking.status is BookingStatus.CANCELED_BY_STAFF
        ):
            booking.send_cancellation_email()
        booking_serializer = BookingSerializer(booking)
        return Response(booking_serializer.data, status=HTTP_200_OK)
