import os
from typing import Any, cast

import stripe
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import GenericViewSet

from customer.models import Customer
from user.models import CustomUser

from .enums import BookingStatus
from .errors import BOOKING_ALREADY_CANCELED_ERROR, BOOKING_CANCEL_COMPLETED_ERROR
from .models import Booking
from .permissions import IsBookingOwner
from .serializers import BookingSerializer
from .services import BookingService

stripe.api_key = os.getenv("STRIPE_API_KEY")


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

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create a booking. Automatically creates user and/or customer"""

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            service = BookingService(
                address_city=serializer.validated_data.get("address_city"),
                address_country=serializer.validated_data.get("address_country"),
                address_line1=serializer.validated_data.get("address_line1"),
                address_postal_code=serializer.validated_data.get(
                    "address_postal_code"
                ),
                car=serializer.validated_data.get("car"),
                email=serializer.validated_data.get("email"),
                end_date=serializer.validated_data.get("end_date"),
                first_name=serializer.validated_data.get("first_name"),
                last_name=serializer.validated_data.get("last_name"),
                phone=serializer.validated_data.get("phone"),
                price_cents=serializer.validated_data.get("price_cents"),
                start_date=serializer.validated_data.get("start_date"),
                address_line2=serializer.validated_data.get("address_line2"),
                address_state=serializer.validated_data.get("address_state"),
                passport=serializer.validated_data.get("passport"),
            )
            booking = service.create()
            headers = self.get_success_headers(serializer.data)
            return Response(
                self.get_serializer(booking).data,
                status=HTTP_201_CREATED,
                headers=headers,
            )
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def create_payment_intent(
        self, request: Request, *args: Any, **kwargs: str
    ) -> Response:
        """Create a Stripe payment intent to pay a booking"""

        # Check permissions
        self.permission_classes = [IsBookingOwner]
        booking = get_object_or_404(Booking, pk=kwargs["pk"])
        self.check_object_permissions(request, booking)

        # Create Stripe payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=booking.price_cents,
            currency="thb",
            customer=booking.customer.stripe_id,
            metadata={"booking_id": str(booking.pk)},
        )

        return Response(payment_intent, status=HTTP_200_OK)

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
