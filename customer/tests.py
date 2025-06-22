from django.db import IntegrityError
from django.forms import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APITestCase

from user.models import CustomUser

from .models import Customer


def set_up_customer():
    user = CustomUser.objects.create(email="paul.doe@gmail.com")
    customer = Customer.objects.create(
        user=user,
        first_name="Paul",
        last_name="Doe",
        address_line1="1135 Felosa Drive",
        address_city="Los Angeles",
        address_postal_code="90063",
        address_state="California",
        address_country="US",
        phone="+14844145698",
        passport="9857460SH",
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
                first_name=self.customer.first_name,
                last_name=self.customer.last_name,
                address_line1=self.customer.address_line1,
                address_city=self.customer.address_city,
                address_postal_code=self.customer.address_postal_code,
                address_state=self.customer.address_state,
                address_country=self.customer.address_country,
                phone=self.customer.phone,
                passport=self.customer.passport,
            )

    def test_create_customer_required_passport(self):
        """Ensures the passport field is required if customer's country is not Thailand"""

        with self.assertRaises(ValidationError):
            user = CustomUser.objects.create(email="lucas.doe@gmail.com")
            Customer.objects.create(
                user=user,
                first_name=self.customer.first_name,
                last_name=self.customer.last_name,
                address_line1=self.customer.address_line1,
                address_city=self.customer.address_city,
                address_postal_code=self.customer.address_postal_code,
                address_state=self.customer.address_state,
                address_country="IT",
                phone=self.customer.phone,
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
