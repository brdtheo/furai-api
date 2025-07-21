import os
from typing import TYPE_CHECKING

import stripe
from django.db import transaction
from django.shortcuts import get_object_or_404

from user.models import CustomUser

from .errors import CUSTOMER_PASSPORT_NUMBER_REQUIRED_ERROR

stripe.api_key = os.getenv("STRIPE_API_KEY")

THAILAND_COUNTRY_CODE = "TH"

if TYPE_CHECKING:
    from .models import Customer


class CustomerService:
    """
    Service class for Customer instances
    """

    def __init__(
        self,
        address_city: str,
        address_country: str,
        address_line1: str,
        address_postal_code: str,
        first_name: str,
        last_name: str,
        phone: str,
        user: CustomUser,
        passport: str = "",
        address_line2: str = "",
        address_state: str = "",
        id: int | None = None,
        stripe_id: str | None = None,
    ) -> None:
        from .models import Customer

        self.model_class = Customer
        self.address_city = address_city
        self.address_country = address_country
        self.address_line1 = address_line1
        self.address_line2 = address_line2
        self.address_postal_code = address_postal_code
        self.address_state = address_state
        self.first_name = first_name
        self.last_name = last_name
        self.passport = passport
        self.phone = phone
        self.user = user
        self.id = id
        self.stripe_id = stripe_id

    def validate_passport(self, address_country: str, passport: str = "") -> None:
        """Raise an error if customer is a foreign national and passport number is empty"""

        if address_country != THAILAND_COUNTRY_CODE and not passport:
            raise CUSTOMER_PASSPORT_NUMBER_REQUIRED_ERROR

    @transaction.atomic
    def create(self) -> "Customer":
        self.validate_passport(self.address_country, self.passport)

        stripe_customer = stripe.Customer.create(
            name=f"{self.first_name} {self.last_name}",
            email=self.user.email,
            address={
                "city": self.address_city,
                "country": self.address_country,
                "line1": self.address_line1,
                "line2": self.address_line2,
                "postal_code": self.address_postal_code,
                "state": self.address_state,
            },
            phone=self.phone,
        )

        customer = super(
            self.model_class._default_manager.__class__,
            self.model_class._default_manager,
        ).create(
            address_city=self.address_city,
            address_country=self.address_country,
            address_line1=self.address_line1,
            address_line2=self.address_line2,
            address_postal_code=self.address_postal_code,
            address_state=self.address_state,
            first_name=self.first_name,
            last_name=self.last_name,
            passport=self.passport,
            phone=self.phone,
            stripe_id=stripe_customer.id,
            user=self.user,
        )

        return customer

    @transaction.atomic
    def update(self) -> "Customer":
        self.validate_passport(self.address_country, self.passport)

        customer = get_object_or_404(self.model_class, pk=self.id)

        stripe.Customer.modify(
            customer.stripe_id,
            name=f"{self.first_name} {self.last_name}",
            email=self.user.email,
            address={
                "city": self.address_city,
                "country": self.address_country,
                "line1": self.address_line1,
                "line2": self.address_line2,
                "postal_code": self.address_postal_code,
                "state": self.address_state,
            },
            phone=self.phone,
        )

        (
            super(  # type: ignore
                self.model_class._default_manager.__class__,
                self.model_class._default_manager,
            )
            .filter(pk=self.id)
            .update(
                address_city=self.address_city,
                address_country=self.address_country,
                address_line1=self.address_line1,
                address_line2=self.address_line2,
                address_postal_code=self.address_postal_code,
                address_state=self.address_state,
                first_name=self.first_name,
                last_name=self.last_name,
                passport=self.passport,
                phone=self.phone,
                user=self.user,
            )
        )

        return customer
