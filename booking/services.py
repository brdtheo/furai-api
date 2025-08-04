import os
from datetime import datetime
from typing import Any, cast

import resend
import stripe
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from resend.emails._email import Email

from booking.enums import BookingStatus
from car.models import CarMedia
from customer.models import Customer
from customer.services import CustomerService
from furai.settings import CURRENCY, NOREPLY_EMAIL_ADDRESS
from user.models import CustomUser

from .errors import (
    BOOKING_ALREADY_CANCELED_ERROR,
    BOOKING_CANCEL_COMPLETED_ERROR,
    BOOKING_CAR_UNAVAILABLE_TIME_PERIOD_ERROR,
    BOOKING_END_DATE_BEFORE_START_DATE_ERROR,
    BOOKING_END_DATE_IN_THE_PAST_ERROR,
    BOOKING_NEGATIVE_PRICE_ERROR,
    BOOKING_SAME_DAY_BOOKING_ERROR,
    BOOKING_START_DATE_IN_THE_PAST_ERROR,
)
from .models import Booking

stripe.api_key = os.getenv("STRIPE_API_KEY")


class BookingService:
    """
    Service class for Booking instances
    """

    def __init__(
        self,
        address_city: str | None = None,
        address_country: str | None = None,
        address_line1: str | None = None,
        address_postal_code: str | None = None,
        car: int | None = None,
        email: str | None = None,
        end_date: datetime | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
        price_cents: int | None = None,
        start_date: datetime | None = None,
        address_line2: str | None = None,
        address_state: str | None = None,
        passport: str | None = None,
        id: int | None = None,
    ) -> None:
        self.address_city = address_city
        self.address_country = address_country
        self.address_line1 = address_line1
        self.address_postal_code = address_postal_code
        self.car = car
        self.email = email
        self.end_date = end_date
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.price_cents = price_cents
        self.start_date = start_date
        self.address_line2 = address_line2
        self.address_state = address_state
        self.passport = passport
        self.id = id

    def send_confirmation_email(self, booking: Booking) -> Email:
        """Send an email to the user when a new Booking is created"""

        queryset = CarMedia.objects.filter(car=booking.car, is_thumbnail=True)
        car_thumbnail = queryset[0].url if queryset.exists() else None
        html_body = render_to_string(
            "booking-confirmation.html",
            {
                "start_date": booking.start_date,
                "end_date": booking.end_date,
                "car_thumbnail": car_thumbnail,
                "car_name": booking.car.name,
                "status": booking.status,
            },
        )
        params: resend.Emails.SendParams = {
            "from": NOREPLY_EMAIL_ADDRESS,
            "to": [booking.customer.user.email],
            "subject": "Your booking confirmation",
            "html": html_body,
        }
        return resend.Emails.send(params)

    def send_cancellation_email(self, booking: Booking) -> Email:
        """Send an email to the user when a Booking is cancelled"""

        queryset = CarMedia.objects.filter(car=booking.car, is_thumbnail=True)
        car_thumbnail = queryset[0].url if queryset.exists() else None
        html_body = render_to_string(
            "booking-cancellation.html",
            {
                "start_date": booking.start_date,
                "end_date": booking.end_date,
                "car_thumbnail": car_thumbnail,
                "car_name": booking.car.name,
                "status": booking.status,
            },
        )
        params: resend.Emails.SendParams = {
            "from": NOREPLY_EMAIL_ADDRESS,
            "to": [booking.customer.user.email],
            "subject": "Your booking has been cancelled",
            "html": html_body,
        }
        return resend.Emails.send(params)

    def create_payment_intent(self) -> stripe.PaymentIntent:
        """Create a Stripe payment intent from a booking"""

        booking = get_object_or_404(Booking, pk=self.id)
        payment_intent = stripe.PaymentIntent.create(
            amount=booking.price_cents,
            currency=CURRENCY.lower(),
            customer=booking.customer.stripe_id,
            metadata={"booking_id": str(booking.pk)},
        )
        return payment_intent

    @transaction.atomic
    def create(self) -> Booking:
        # Raise an error if the price is negative
        if self.price_cents is not None and self.price_cents < 0:
            raise BOOKING_NEGATIVE_PRICE_ERROR

        # Raise an error if one of the dates is in the past
        if self.start_date is not None and self.end_date is not None:
            if self.start_date < timezone.now():
                raise BOOKING_START_DATE_IN_THE_PAST_ERROR
            if self.end_date < timezone.now():
                raise BOOKING_END_DATE_IN_THE_PAST_ERROR

        # Raise an error if the end date is before the start date
        if (
            self.end_date is not None
            and self.start_date is not None
            and self.end_date < self.start_date
        ):
            raise BOOKING_END_DATE_BEFORE_START_DATE_ERROR

        # Raise an error if start date is on the same day
        if (
            self.start_date is not None
            and self.start_date.date().day == timezone.now().day
        ):
            raise BOOKING_SAME_DAY_BOOKING_ERROR

        # Raise an error if the car is unavailable in the requested time period
        if Booking.objects.filter(
            car=self.car,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date,
        ).exists():
            raise BOOKING_CAR_UNAVAILABLE_TIME_PERIOD_ERROR

        try:
            user = CustomUser.objects.get(email=self.email)
        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create(email=cast(str, self.email))

        customer_service_data: dict[str, Any] = {
            "user": user,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address_line1": self.address_line1,
            "address_city": self.address_city,
            "address_postal_code": self.address_postal_code,
            "address_country": self.address_country,
            "phone": self.phone,
            "passport": self.passport,
            "address_line2": self.address_line2,
            "address_state": self.address_state,
        }

        try:
            customer = Customer.objects.get(user=user)
            customer_service = CustomerService(
                **customer_service_data,
                id=customer.pk,
            )
            customer_service.update()
        except Customer.DoesNotExist:
            customer_service = CustomerService(**customer_service_data)
            customer = customer_service.create()

        booking = Booking(  # type: ignore
            car=self.car,
            customer=customer,
            start_date=self.start_date,
            end_date=self.end_date,
            price_cents=self.price_cents,
        )
        booking.save()

        self.send_confirmation_email(booking)

        return booking

    @transaction.atomic
    def cancel(self, is_staff_origin: bool = False) -> Booking:
        """Cancel a booking"""

        booking = get_object_or_404(Booking, pk=self.id)

        if booking.status == BookingStatus.COMPLETED:
            raise BOOKING_CANCEL_COMPLETED_ERROR
        if booking.status == (
            BookingStatus.CANCELED_BY_CUSTOMER or BookingStatus.CANCELED_BY_STAFF
        ):
            raise BOOKING_ALREADY_CANCELED_ERROR

        booking.mark_as_cancelled(is_staff_origin)
        self.send_cancellation_email(booking)

        return booking
