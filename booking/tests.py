import random
from datetime import timedelta, timezone

from django.forms import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone as django_timezone
from faker import Faker
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from rest_framework.test import APITestCase

from car.models import Car
from car.tests import set_up_car
from customer.tests import set_up_customer, set_up_customer_list
from furai.tests.utils import TestClientAuthenticator

from .enums import BookingStatus
from .models import Booking

fake = Faker()

# A safe start date to prevent raising error from same day booking
secure_start_date = fake.future_datetime(tzinfo=timezone.utc) + timedelta(days=2)


def set_up_booking(car, customer):
    """Creates a Booking instance in the test DB"""

    booking = Booking.objects.create(
        car=car,
        customer=customer,
        start_date=secure_start_date,
        end_date=secure_start_date + timedelta(hours=6),
        status=BookingStatus.CONFIRMED,
    )
    return booking


def set_up_booking_list():
    """Creates several Booking instances in the test DB"""

    customer_list = set_up_customer_list()
    booking_list = []
    car_count = Car.objects.count()
    for customer in customer_list:
        """Creates a booking for each customer from a random car"""
        booking = Booking.objects.create(
            car=Car.objects.all()[random.randint(0, car_count - 1)],
            customer=customer,
            start_date=secure_start_date,
            end_date=secure_start_date + timedelta(hours=6),
            status=BookingStatus.CONFIRMED,
        )
        booking_list.append(booking)
    return booking_list


class BookingTestCase(TestCase):
    def setUp(self):
        car = set_up_car()
        customer = set_up_customer()
        set_up_booking_list()
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
        set_up_booking_list()
        self.car = car
        self.customer = customer

    def test_get_booking_list_unauthenticated(self):
        """Prevent listing bookings if not authenticated"""

        url = reverse("booking-list")
        response = self.client.get(url, format="json")
        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_get_booking_list(self):
        """Correctly list all bookings related to a customer"""

        TestClientAuthenticator.authenticate(self.client, self.customer.user)
        url = reverse("booking-list")
        response = self.client.get(url, format="json")
        assert response.status_code == HTTP_200_OK
        for booking in response.data["results"]:
            assert booking.customer == self.customer
        TestClientAuthenticator.authenticate_logout(self.client)
