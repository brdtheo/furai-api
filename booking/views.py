from typing import Any, cast

from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import GenericViewSet

from customer.models import Customer
from user.models import CustomUser

from .enums import BookingStatus
from .errors import BOOKING_ALREADY_CANCELED_ERROR, BOOKING_CANCEL_COMPLETED_ERROR
from .models import Booking
from .permissions import IsBookingOwner
from .serializers import BookingSerializer


class BookingViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    """
    List all bookings related to a customer or create Bookings
    """

    serializer_class = BookingSerializer

    def get_queryset(self) -> QuerySet[Booking]:
        user: CustomUser = cast(
            CustomUser,
            self.request.user,
        )
        customer = get_object_or_404(Customer, user=user.pk)
        queryset = Booking.objects.filter(customer=customer).order_by("-created_at")
        return queryset

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """List all bookings related to a customer"""

        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer: BaseSerializer) -> None:
        """
        Create a new booking and send a confirmation email.
        Automatically create the user if none associated to the email.
        Automatically create/update a customer with payload infos.
        """
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
