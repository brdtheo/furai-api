from django.test import TestCase
from django.urls import reverse
from faker import Faker
from rest_framework.exceptions import ValidationError
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from rest_framework.test import APITestCase

from furai.tests.mocks import enable_stripe_mock
from furai.tests.utils import TestClientAuthenticator
from user.models import CustomUser

from .models import Customer

fake = Faker()


def set_up_customer():
    """Creates a CustomUser and Customer instance in the test DB"""

    first_name = fake.first_name()
    last_name = fake.last_name()
    email = f"{first_name}.{last_name}@{fake.domain_name()}"
    user = CustomUser.objects.create(email=email)
    customer = Customer.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        address_line1=fake.street_address(),
        address_city=fake.city(),
        address_postal_code=fake.postalcode(),
        address_state=fake.state(),
        address_country=fake.country_code(),
        phone=fake.phone_number(),
        passport=fake.passport_number(),
    )
    return customer


def set_up_customer_list():
    """Creates several random CustomUser and related Customer instances in the test DB"""

    user_list = []
    for i in range(10):
        user = CustomUser.objects.create(
            email=f"{fake.first_name()}.{fake.last_name()}@{fake.domain_name()}"
        )
        user_list.append(user)
    customer_list = []
    for user in user_list:
        customer = Customer.objects.create(
            user=user,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            address_line1=fake.street_address(),
            address_city=fake.city(),
            address_postal_code=fake.postalcode(),
            address_state=fake.state(),
            address_country="US",
            phone=fake.phone_number(),
            passport=fake.passport_number(),
        )
        customer_list.append(customer)
    return customer_list


class CustomerTestCase(TestCase):
    def setUp(self):
        enable_stripe_mock(self)
        customer = set_up_customer()
        self.customer = customer
        self.user = customer.user

    def test_create_customer_no_user(self):
        """Ensures a customer cannot be created without a linked user"""

        with self.assertRaises(TypeError):
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

    def test_representation_string(self):
        """Returns the instance representation correctly"""

        assert (
            self.customer.__str__()
            == f"{self.customer.first_name} {self.customer.last_name}"
        )


class CustomerAPITestCase(APITestCase):
    def setUp(self):
        enable_stripe_mock(self)
        customer = set_up_customer()
        self.customer = customer
        self.user = customer.user

    def test_retrieve_current_customer(self):
        """Correctly retrieves the customer instance linked to the current user"""

        TestClientAuthenticator.authenticate(self.client, self.user)
        url = reverse("customers-me")
        response = self.client.get(url, format="json")
        assert response.status_code == HTTP_200_OK
        assert response.data["user"] == self.user.id
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
        TestClientAuthenticator.authenticate_logout(self.client)

    def test_retrieve_current_customer_unauthenticated(self):
        """Prevent retrieving the current customer if not authenticated"""

        url = reverse("customers-me")
        response = self.client.get(url, format="json")
        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_update_customer(self):
        """Correctly update a customer instance"""

        TestClientAuthenticator.authenticate(self.client, self.user)
        url = reverse("customers-detail", kwargs={"pk": self.customer.id})
        first_name = fake.first_name()
        response = self.client.patch(
            url, data={"first_name": first_name}, format="json"
        )
        assert response.status_code == HTTP_200_OK
        self.customer.refresh_from_db()
        assert self.customer.first_name == first_name
        TestClientAuthenticator.authenticate_logout(self.client)

    def test_update_customer_unauthenticated(self):
        """Prevent updating the current customer if not authenticated"""

        url = reverse("customers-detail", kwargs={"pk": self.customer.id})
        response = self.client.patch(
            url, data={"first_name": fake.first_name()}, format="json"
        )
        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_update_customer_not_authorized(self):
        """Prevent updating the current customer if user is not linked to it"""

        random_customer = set_up_customer()
        TestClientAuthenticator.authenticate(self.client, random_customer.user)
        url = reverse("customers-detail", kwargs={"pk": self.customer.id})
        response = self.client.patch(
            url, data={"first_name": fake.first_name()}, format="json"
        )
        assert response.status_code == HTTP_403_FORBIDDEN
        TestClientAuthenticator.authenticate_logout(self.client)
