from datetime import datetime
from typing import Any, cast

from django.db import transaction
from django.utils import timezone

from customer.models import Customer
from customer.services import CustomerService
from user.models import CustomUser

from .errors import (
    BOOKING_CAR_UNAVAILABLE_TIME_PERIOD_ERROR,
    BOOKING_END_DATE_BEFORE_START_DATE_ERROR,
    BOOKING_END_DATE_IN_THE_PAST_ERROR,
    BOOKING_NEGATIVE_PRICE_ERROR,
    BOOKING_SAME_DAY_BOOKING_ERROR,
    BOOKING_START_DATE_IN_THE_PAST_ERROR,
)
from .models import Booking


class BookingService:
    """
    Service class for Booking instances
    """

    def __init__(
        self,
        address_city: str,
        address_country: str,
        address_line1: str,
        address_postal_code: str,
        car: int,
        email: str,
        end_date: datetime,
        first_name: str,
        last_name: str,
        phone: str,
        price_cents: int,
        start_date: datetime,
        address_line2: str = "",
        address_state: str = "",
        passport: str = "",
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
        if self.end_date is not None and self.end_date < self.start_date:
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

        return booking
