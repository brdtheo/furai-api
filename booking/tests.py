from datetime import timedelta, timezone

from django.forms import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone as django_timezone
from faker import Faker
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APITestCase

from car.tests import set_up_car
from customer.tests import set_up_customer

from .enums import BookingStatus
from .models import Booking

fake = Faker()


def set_up_booking(car, customer):
    """Creates a Booking instance in the test DB"""

    start_date = fake.future_datetime(tzinfo=timezone.utc)
    booking = Booking.objects.create(
        car=car,
        customer=customer,
        start_date=start_date,
        end_date=start_date + timedelta(hours=6),
        status=BookingStatus.CONFIRMED,
    )
    return booking


class BookingTestCase(TestCase):
    def setUp(self):
        car = set_up_car()
        customer = set_up_customer()
        booking = set_up_booking(car, customer)
        self.car = car
        self.customer = customer
        self.booking = booking

    def test_create_booking_start_date_past(self):
        """Ensures a booking cannot be created if start date is in the past"""

        with self.assertRaises(ValidationError):
            start_date = fake.past_datetime(tzinfo=timezone.utc)
            Booking.objects.create(
                car=self.car,
                customer=self.customer,
                start_date=start_date,
                end_date=fake.future_datetime(tzinfo=timezone.utc),
                status=BookingStatus.CONFIRMED,
            )

    def test_create_booking_start_date_same_day(self):
        """Ensures a booking cannot be created if start date is current day"""

        with self.assertRaises(ValidationError):
            start_date = django_timezone.now()
            Booking.objects.create(
                car=self.car,
                customer=self.customer,
                start_date=start_date,
                end_date=fake.future_datetime(tzinfo=timezone.utc),
                status=BookingStatus.CONFIRMED,
            )

    def test_update_booking_status(self):
        """Ensures a booking status can be updated correctly"""

        self.booking.status = BookingStatus.COMPLETED
        self.booking.save()
        assert self.booking.status == BookingStatus.COMPLETED


class BookingAPITestCase(APITestCase):
    def setUp(self):
        car = set_up_car()
        customer = set_up_customer()
        booking = set_up_booking(car, customer)
        self.car = car
        self.customer = customer
        self.booking = booking

    def test_get_booking_list(self):
        """Correctly list all bookings correctly"""

        url = reverse("booking-list")
        response = self.client.get(url, format="json")
        assert response.status_code == HTTP_200_OK
