from django.db import IntegrityError
from django.forms import ValidationError
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APITestCase

from user.models import CustomUser

from .models import Customer

fake = Faker()


def set_up_customer():
    """Creates a User and Cusomer instance in the test DB"""

    first_name = fake.first_name()
    last_name = fake.last_name()
    email = f"{first_name}.{last_name}@{fake.domain_name}"
    user = CustomUser.objects.create(email=email)
    customer = Customer.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        address_line1=fake.street_address(),
        address_city=fake.city(),
        address_postal_code=fake.postalcode(),
        address_state=fake.state(),
        address_country="US",
        phone=fake.phone_number(),
        passport=fake.passport_number(),
    )
    return customer


class CustomerTestCase(TestCase):
    def setUp(self):
        customer = set_up_customer()
        self.customer = customer

    def test_create_customer_no_user(self):
        """Ensures a customer cannot be created without a linked user"""

        with self.assertRaises(IntegrityError):
            Customer.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                address_line1=fake.street_address(),
                address_city=fake.city(),
                address_postal_code=fake.postalcode(),
                address_state=fake.state(),
                address_country=fake.country_code(),
                phone=fake.phone_number(),
                passport=fake.passport_number(),
            )

    def test_create_customer_required_passport(self):
        """Ensures the passport field is required if customer's country is not Thailand"""

        with self.assertRaises(ValidationError):
            user = CustomUser.objects.create(email=fake.email())
            Customer.objects.create(
                user=user,
                first_name=self.customer.first_name,
                last_name=self.customer.last_name,
                address_line1=fake.street_address(),
                address_city=fake.city(),
                address_postal_code=fake.postalcode(),
                address_state=fake.state(),
                address_country="IT",
                phone=fake.phone_number(),
            )


class CustomerAPITestCase(APITestCase):
    def setUp(self):
        customer = set_up_customer()
        self.customer = customer

    def test_retrieve_customer(self):
        """Correctly retrieves a customer instance"""

        url = reverse("customer-detail", kwargs={"pk": self.customer.pk})
        response = self.client.get(url, format="json")
        assert response.status_code == HTTP_200_OK
        assert response.data["first_name"] == self.customer.first_name
        assert response.data["last_name"] == self.customer.last_name
        assert response.data["address_line1"] == self.customer.address_line1
        assert response.data["address_line2"] == self.customer.address_line2
        assert response.data["address_city"] == self.customer.address_city
        assert response.data["address_postal_code"] == self.customer.address_postal_code
        assert response.data["address_state"] == self.customer.address_state
        assert response.data["address_country"] == self.customer.address_country
        assert response.data["phone"] == self.customer.phone
        assert response.data["passport"] == self.customer.passport
