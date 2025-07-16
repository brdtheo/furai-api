import random
import re
from datetime import datetime, timedelta, timezone

from django.test import TestCase
from faker import Faker
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)
from rest_framework.test import APITestCase

from car.models import Car
from car.tests import set_up_car
from customer.models import Customer
from customer.tests import set_up_customer, set_up_customer_list
from furai.tests.mocks import enable_stripe_mock
from furai.tests.utils import TestClientAuthenticator
from user.models import CustomUser

from .enums import BookingStatus
from .errors import (
    BOOKING_ALREADY_CANCELED_ERROR,
    BOOKING_CANCEL_COMPLETED_ERROR,
    BOOKING_CAR_UNAVAILABLE_TIME_PERIOD_ERROR,
    BOOKING_CUSTOMER_PASSPORT_REQUIRED_ERROR,
    BOOKING_END_DATE_BEFORE_START_DATE_ERROR,
    BOOKING_END_DATE_IN_THE_PAST_ERROR,
    BOOKING_NEGATIVE_PRICE_ERROR,
    BOOKING_SAME_DAY_BOOKING_ERROR,
    BOOKING_START_DATE_IN_THE_PAST_ERROR,
)
from .models import Booking

fake = Faker()

# Safe dates to prevent raising error from same day booking
secure_future_date = fake.future_datetime(tzinfo=timezone.utc) + timedelta(days=2)
secure_past_date = fake.past_datetime(tzinfo=timezone.utc) - timedelta(days=2)
secure_booking_start_date = fake.future_datetime(tzinfo=timezone.utc) + timedelta(
    days=3
)
secure_booking_end_date = secure_booking_start_date + timedelta(hours=3)


def set_up_booking(car, customer):
    """Creates a Booking instance in the test DB"""

    booking = Booking.objects.create(
        car=car,
        price_cents=fake.pyint(300000, 1000000),
        customer=customer,
        start_date=secure_future_date,
        end_date=secure_future_date + timedelta(hours=6),
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
            price_cents=fake.pyint(300000, 1000000),
            customer=customer,
            start_date=secure_future_date,
            end_date=secure_future_date + timedelta(hours=6),
            status=BookingStatus.CONFIRMED,
        )
        booking_list.append(booking)
    return booking_list


class BookingTestCase(TestCase):
    def setUp(self):
        enable_stripe_mock(self)
        car = set_up_car()
        customer = set_up_customer()
        set_up_booking_list()
        booking = set_up_booking(car, customer)
        self.car = car
        self.customer = customer
        self.booking = booking

    def test_update_booking_status(self):
        """Ensures a booking status can be updated correctly"""

        self.booking.status = BookingStatus.COMPLETED
        self.booking.save()
        assert self.booking.status == BookingStatus.COMPLETED

    def test_cancel_booking_by_customer(self):
        """Ensures a booking is cancelled correctly by a customer"""

        self.booking.cancel()
        assert self.booking.status == BookingStatus.CANCELED_BY_CUSTOMER

    def test_cancel_booking_by_staff(self):
        """Ensures a booking is cancelled correctly by a staff member"""

        self.booking.cancel(True)
        assert self.booking.status == BookingStatus.CANCELED_BY_STAFF


class BookingAPITestCase(APITestCase):
    def setUp(self):
        enable_stripe_mock(self)
        car = set_up_car()
        customer = set_up_customer()
        booking = set_up_booking(car, customer)
        booking_list = set_up_booking_list()
        self.car = car
        self.customer = customer
        self.booking = booking
        self.booking_list = booking_list

    def test_get_booking_list_unauthenticated(self):
        """Prevent listing bookings if not authenticated"""

        url = reverse("bookings-list")
        response = self.client.get(url, format="json")
        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_get_booking_list(self):
        """Correctly list all bookings related to a customer"""

        TestClientAuthenticator.authenticate(self.client, self.customer.user)
        url = reverse("bookings-list")
        response = self.client.get(url, format="json")
        assert response.status_code == HTTP_200_OK
        for booking in response.data["results"]:
            assert booking["customer"] == self.customer.id
        TestClientAuthenticator.authenticate_logout(self.client)

    def test_create_booking_negative_price(self):
        """Return an error error if price is negative"""

        url = reverse("bookings-list")
        response = self.client.post(
            url,
            data={
                "start_date": secure_booking_start_date,
                "end_date": secure_booking_end_date,
                "car": self.car.pk,
                "price_cents": fake.pyint(-10000, -1),
                "email": self.customer.user.email,
                "first_name": self.customer.first_name,
                "last_name": self.customer.last_name,
                "address_line1": self.customer.address_line1,
                "address_line2": self.customer.address_line2,
                "address_city": self.customer.address_city,
                "address_postal_code": self.customer.address_postal_code,
                "address_state": self.customer.address_state,
                "address_country": "US",
                "phone": self.customer.phone,
                "passport": self.customer.passport,
            },
            format="json",
        )
        assert response.status_code == HTTP_400_BAD_REQUEST
        assert re.match(
            BOOKING_NEGATIVE_PRICE_ERROR.detail["price_cents"].title().lower(),
            response.data["price_cents"][0].lower(),
        )

    def test_create_booking_start_date_same_day(self):
        """Return an error error if start date is current day"""

        url = reverse("bookings-list")
        response = self.client.post(
            url,
            data={
                "start_date": (
                    datetime.now(tz=timezone.utc) + timedelta(hours=1)
                ).isoformat(),
                "end_date": secure_booking_end_date,
                "car": self.car.pk,
                "price_cents": fake.pyint(300000, 1000000),
                "email": self.customer.user.email,
                "first_name": self.customer.first_name,
                "last_name": self.customer.last_name,
                "address_line1": self.customer.address_line1,
                "address_line2": self.customer.address_line2,
                "address_city": self.customer.address_city,
                "address_postal_code": self.customer.address_postal_code,
                "address_state": self.customer.address_state,
                "address_country": "US",
                "phone": self.customer.phone,
                "passport": self.customer.passport,
            },
            format="json",
        )
        assert response.status_code == HTTP_400_BAD_REQUEST
        assert (
            re.match(
                BOOKING_SAME_DAY_BOOKING_ERROR.detail[0].title().lower(),
                response.data["non_field_errors"][0].lower(),
            )
            is not None
        )

    def test_create_booking_start_date_past(self):
        """Return an error if the start date is in the past"""

        url = reverse("bookings-list")
        response = self.client.post(
            url,
            data={
                "start_date": secure_past_date,
                "end_date": secure_booking_end_date,
                "car": self.car.pk,
                "price_cents": fake.pyint(300000, 1000000),
                "email": self.customer.user.email,
                "first_name": self.customer.first_name,
                "last_name": self.customer.last_name,
                "address_line1": self.customer.address_line1,
                "address_line2": self.customer.address_line2,
                "address_city": self.customer.address_city,
                "address_postal_code": self.customer.address_postal_code,
                "address_state": self.customer.address_state,
                "address_country": "US",
                "phone": self.customer.phone,
                "passport": self.customer.passport,
            },
            format="json",
        )
        assert response.status_code == HTTP_400_BAD_REQUEST
        assert (
            re.match(
                BOOKING_START_DATE_IN_THE_PAST_ERROR.detail[0].title().lower(),
                response.data["non_field_errors"][0].lower(),
            )
            is not None
        )

    def test_create_booking_end_date_past(self):
        """Return an error if the end date is in the past"""

        url = reverse("bookings-list")
        response = self.client.post(
            url,
            data={
                "start_date": secure_booking_start_date,
                "end_date": secure_past_date,
                "car": self.car.pk,
                "price_cents": fake.pyint(300000, 1000000),
                "email": self.customer.user.email,
                "first_name": self.customer.first_name,
                "last_name": self.customer.last_name,
                "address_line1": self.customer.address_line1,
                "address_line2": self.customer.address_line2,
                "address_city": self.customer.address_city,
                "address_postal_code": self.customer.address_postal_code,
                "address_state": self.customer.address_state,
                "address_country": "US",
                "phone": self.customer.phone,
                "passport": self.customer.passport,
            },
            format="json",
        )
        assert response.status_code == HTTP_400_BAD_REQUEST
        assert (
            re.match(
                BOOKING_END_DATE_IN_THE_PAST_ERROR.detail[0].title().lower(),
                response.data["non_field_errors"][0].lower(),
            )
            is not None
        )

    def test_create_booking_end_date_before_start_date(self):
        """Return an error if the end date is before the the start date"""

        url = reverse("bookings-list")
        response = self.client.post(
            url,
            data={
                "start_date": secure_booking_start_date,
                "end_date": secure_booking_start_date - timedelta(hours=6),
                "car": self.car.pk,
                "price_cents": fake.pyint(300000, 1000000),
                "email": self.customer.user.email,
                "first_name": self.customer.first_name,
                "last_name": self.customer.last_name,
                "address_line1": self.customer.address_line1,
                "address_line2": self.customer.address_line2,
                "address_city": self.customer.address_city,
                "address_postal_code": self.customer.address_postal_code,
                "address_state": self.customer.address_state,
                "address_country": "US",
                "phone": self.customer.phone,
                "passport": self.customer.passport,
            },
            format="json",
        )
        assert response.status_code == HTTP_400_BAD_REQUEST
        assert (
            re.match(
                BOOKING_END_DATE_BEFORE_START_DATE_ERROR.detail[0].title().lower(),
                response.data["non_field_errors"][0].lower(),
            )
            is not None
        )

    def test_create_booking_required_passport(self):
        """Return an error error if customer is a foreign national and passport number is empty"""

        url = reverse("bookings-list")
        response = self.client.post(
            url,
            data={
                "start_date": secure_booking_start_date,
                "end_date": secure_booking_end_date,
                "car": self.car.pk,
                "price_cents": fake.pyint(300000, 1000000),
                "email": self.customer.user.email,
                "first_name": self.customer.first_name,
                "last_name": self.customer.last_name,
                "address_line1": self.customer.address_line1,
                "address_line2": self.customer.address_line2,
                "address_city": self.customer.address_city,
                "address_postal_code": self.customer.address_postal_code,
                "address_state": self.customer.address_state,
                "address_country": "IT",
                "phone": self.customer.phone,
                "passport": "",
            },
            format="json",
        )
        assert response.status_code == HTTP_400_BAD_REQUEST
        assert (
            re.match(
                BOOKING_CUSTOMER_PASSPORT_REQUIRED_ERROR.detail[0].title().lower(),
                response.data["non_field_errors"][0].lower(),
            )
            is not None
        )

    def test_create_booking_invalid_country_code(self):
        """Return an error if customer's country is not a valid country"""
        url = reverse("bookings-list")
        response = self.client.post(
            url,
            data={
                "start_date": secure_booking_start_date,
                "end_date": secure_booking_end_date,
                "car": self.car.pk,
                "price_cents": fake.pyint(300000, 1000000),
                "email": self.customer.user.email,
                "first_name": self.customer.first_name,
                "last_name": self.customer.last_name,
                "address_line1": self.customer.address_line1,
                "address_line2": self.customer.address_line2,
                "address_city": self.customer.address_city,
                "address_postal_code": self.customer.address_postal_code,
                "address_state": self.customer.address_state,
                "address_country": "ZZ",
                "phone": self.customer.phone,
                "passport": self.customer.passport,
            },
            format="json",
        )
        assert response.status_code == HTTP_400_BAD_REQUEST
        assert (
            re.search(
                "is not a valid choice",
                response.data["address_country"][0].title().lower(),
            )
            is not None
        )

    def test_create_booking_new_user(self):
        """Create a new user along with booking when no user is associated to the email"""

        url = reverse("bookings-list")
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name}.{last_name}@{fake.domain_name()}"
        response = self.client.post(
            url,
            data={
                "start_date": secure_booking_start_date,
                "end_date": secure_booking_end_date,
                "car": self.car.pk,
                "price_cents": fake.pyint(300000, 1000000),
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "address_line1": fake.street_address(),
                "address_line2": "",
                "address_city": fake.city(),
                "address_postal_code": fake.postcode(),
                "address_state": "",
                "address_country": fake.country_code(),
                "phone": f"{fake.country_calling_code()}{fake.msisdn()}",
                "passport": fake.passport_number(),
            },
            format="json",
        )
        assert response.status_code == HTTP_201_CREATED
        assert CustomUser.objects.get(email=email)

    def test_create_booking_new_customer(self):
        """Create a new customer along with booking when no customer is associated to the email"""

        url = reverse("bookings-list")
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name}.{last_name}@{fake.domain_name()}"
        response = self.client.post(
            url,
            data={
                "start_date": secure_booking_start_date,
                "end_date": secure_booking_end_date,
                "car": self.car.pk,
                "price_cents": fake.pyint(300000, 1000000),
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "address_line1": fake.street_address(),
                "address_line2": "",
                "address_city": fake.city(),
                "address_postal_code": fake.postcode(),
                "address_state": "",
                "address_country": fake.country_code(),
                "phone": f"{fake.country_calling_code()}{fake.msisdn()}",
                "passport": fake.passport_number(),
            },
            format="json",
        )
        assert response.status_code == HTTP_201_CREATED
        customer = Customer.objects.get(user__email=email)
        assert customer.first_name == first_name
        assert customer.last_name == last_name
        assert customer.user.email == email

    def test_create_booking_override_customer_info(self):
        """Correctly override customer informations by booking request payload"""

        url = reverse("bookings-list")
        address_line1 = fake.street_address()
        address_city = fake.city()
        address_postal_code = fake.postcode()
        address_country = fake.country_code()
        phone = f"{fake.country_calling_code()}{fake.msisdn()}"
        response = self.client.post(
            url,
            data={
                "start_date": secure_booking_start_date,
                "end_date": secure_booking_end_date,
                "car": self.car.pk,
                "price_cents": fake.pyint(300000, 1000000),
                "email": self.customer.user.email,
                "first_name": self.customer.first_name,
                "last_name": self.customer.last_name,
                "address_line1": address_line1,
                "address_line2": self.customer.address_line2,
                "address_city": address_city,
                "address_postal_code": address_postal_code,
                "address_state": self.customer.address_state,
                "address_country": address_country,
                "phone": phone,
                "passport": self.customer.passport,
            },
            format="json",
        )
        self.customer.refresh_from_db()
        assert response.status_code == HTTP_201_CREATED
        assert self.customer.address_line1 == address_line1
        assert self.customer.address_city == address_city
        assert self.customer.address_postal_code == address_postal_code
        assert self.customer.address_country == address_country
        assert self.customer.phone == phone

    def test_create_booking_car_not_available(self):
        """Return an error if the car is unavailable in the requested time period"""

        base_data = {
            "start_date": secure_booking_start_date,
            "end_date": secure_booking_end_date,
            "car": self.car.pk,
            "price_cents": fake.pyint(300000, 1000000),
            "email": self.customer.user.email,
            "first_name": self.customer.first_name,
            "last_name": self.customer.last_name,
            "address_line1": self.customer.address_line1,
            "address_line2": self.customer.address_line2,
            "address_city": self.customer.address_city,
            "address_postal_code": self.customer.address_postal_code,
            "address_state": self.customer.address_state,
            "address_country": fake.country_code(),
            "phone": self.customer.phone,
            "passport": self.customer.passport,
        }
        Booking.objects.create(
            car=self.car,
            customer=self.customer,
            start_date=secure_booking_start_date,
            end_date=secure_booking_end_date,
            price_cents=base_data.get("price_cents"),
        )

        url = reverse("bookings-list")
        # The requested booking starts before an existing booking ends
        response_overlap_start_date = self.client.post(
            url,
            data={
                **base_data,
                "start_date": secure_booking_end_date - timedelta(minutes=5),
                "end_date": secure_booking_end_date + timedelta(hours=3),
            },
            format="json",
        )
        # The requested booking ends after an existing booking starts
        response_overlap_end_date = self.client.post(
            url,
            data={
                **base_data,
                "start_date": secure_booking_start_date - timedelta(hours=3),
                "end_date": secure_booking_end_date + timedelta(minutes=5),
            },
            format="json",
        )
        # The requested booking time period is inside an existing booking
        response_overlap_within = self.client.post(
            url,
            data={
                **base_data,
                "start_date": secure_booking_start_date + timedelta(minutes=5),
                "end_date": secure_booking_end_date - timedelta(minutes=5),
            },
            format="json",
        )

        response_list = [
            response_overlap_start_date,
            response_overlap_end_date,
            response_overlap_within,
        ]
        for response in response_list:
            assert response.status_code == HTTP_400_BAD_REQUEST
            assert (
                re.match(
                    BOOKING_CAR_UNAVAILABLE_TIME_PERIOD_ERROR.detail[0].title().lower(),
                    response.data["non_field_errors"][0].title().lower(),
                )
                is not None
            )

    def test_cancel_booking_unauthenticated(self):
        """Prevent cancelling a booking if not authenticated"""

        url = reverse("bookings-cancel", kwargs={"pk": self.booking.id})
        response = self.client.post(url, format="json")
        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_cancel_booking_not_authorized(self):
        """Prevent cancelling a booking if user is not the owner"""

        TestClientAuthenticator.authenticate(self.client, self.booking.customer.user)
        url = reverse("bookings-cancel", kwargs={"pk": self.booking_list[0].id})
        response = self.client.post(url, format="json")
        assert response.status_code == HTTP_403_FORBIDDEN
        TestClientAuthenticator.authenticate_logout(self.client)

    def test_cancel_completed_booking(self):
        """Prevent cancelling a booking if completed"""

        self.booking.status = BookingStatus.COMPLETED
        self.booking.save()
        TestClientAuthenticator.authenticate(self.client, self.booking.customer.user)
        url = reverse("bookings-cancel", kwargs={"pk": self.booking.id})
        response = self.client.post(url, format="json")
        assert response.status_code == HTTP_400_BAD_REQUEST
        assert re.match(
            BOOKING_CANCEL_COMPLETED_ERROR.detail["status"].title().lower(),
            response.data["status"].lower(),
        )
        TestClientAuthenticator.authenticate_logout(self.client)

    def test_already_cancelled_booking(self):
        """Prevent cancelling a booking if already cancelled"""

        self.booking.status = BookingStatus.CANCELED_BY_CUSTOMER
        self.booking.save()
        TestClientAuthenticator.authenticate(self.client, self.booking.customer.user)
        url = reverse("bookings-cancel", kwargs={"pk": self.booking.id})
        response = self.client.post(url, format="json")
        assert response.status_code == HTTP_400_BAD_REQUEST
        assert re.match(
            BOOKING_ALREADY_CANCELED_ERROR.detail["status"].title().lower(),
            response.data["status"].lower(),
        )
        TestClientAuthenticator.authenticate_logout(self.client)

    def test_cancel_booking(self):
        """Cancel a booking correctly"""

        TestClientAuthenticator.authenticate(self.client, self.booking.customer.user)
        url = reverse("bookings-cancel", kwargs={"pk": self.booking.id})
        response = self.client.post(url, format="json")
        assert response.status_code == HTTP_200_OK
        assert response.data["status"] == BookingStatus.CANCELED_BY_CUSTOMER
        TestClientAuthenticator.authenticate_logout(self.client)
