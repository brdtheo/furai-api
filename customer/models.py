import os
from typing import Any, cast, override

import stripe
from django.db import IntegrityError, models
from django.forms import ValidationError
from django.utils import timezone
from django_countries.fields import CountryField

from user.models import CustomUser

stripe.api_key = os.getenv("STRIPE_API_KEY")


class CustomerManager(models.Manager):
    def create(self, **kwargs: Any) -> Any:
        if not kwargs.get("user"):
            raise IntegrityError("Cannot create a customer without a user")
        # Automatically create a Stripe customer and link it to created customer
        stripe_customer = stripe.Customer.create(
            name=f"{kwargs['first_name']} {kwargs['last_name']}",
            email=kwargs["user"].email,
            address={
                "city": kwargs.get("address_city", ""),
                "country": kwargs.get("address_country", ""),
                "line1": kwargs.get("address_line1", ""),
                "line2": kwargs.get("address_line2", ""),
                "postal_code": kwargs.get("address_postal_code", ""),
                "state": kwargs.get("address_state", ""),
            },
            phone=kwargs["phone"],
        )
        return super().create(
            **kwargs,
            stripe_id=stripe_customer.id,
        )


class Customer(models.Model):
    """Representation of a Customer"""

    objects = CustomerManager()

    stripe_id = models.CharField(
        help_text="The Stripe customer identifier linked to the customer",
        db_comment="The Stripe customer identifier linked to the customer",
        blank=True,
    )
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        help_text="The user linked to the customer",
        db_comment="The user linked to the customer",
    )
    first_name = models.CharField(
        max_length=50,
        help_text="The customer's first name",
        db_comment="The customer's first name",
    )
    last_name = models.CharField(
        max_length=50,
        help_text="The customer's last name",
        db_comment="The customer's last name",
    )
    address_line1 = models.CharField(
        max_length=100,
        help_text="Address line 1 (e.g. street)",
        db_comment="Address line 1 (e.g. street)",
    )
    address_line2 = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Address line 2 (e.g. apartment, suite, building)",
        db_comment="Address line 2 (e.g. apartment, suite, building)",
    )
    address_city = models.CharField(
        max_length=100,
        help_text="City, district, suburb, town or village",
        db_comment="City, district, suburb, town or village",
    )
    address_postal_code = models.CharField(
        max_length=10,
        help_text="ZIP or postal code",
        db_comment="ZIP or postal code",
    )
    address_state = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="State, county, province or region",
        db_comment="State, county, province or region",
    )
    address_country = CountryField(
        help_text="Customer's country of residence",
        db_comment="Customer's country of residence",
    )
    phone = models.CharField(
        max_length=50,
        help_text="Customer's phone number",
        db_comment="Customer's phone number",
    )
    passport = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Customer's passport number if not Thai citizen",
        db_comment="Customer's passport number if not Thai citizen",
    )
    created_at = models.DateTimeField(
        help_text="The creation date of the customer",
        db_comment="The creation date of the customer",
        default=timezone.now,
    )

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def validate_passport(self) -> None:
        """Ensures the passport field is required if customer's country is not Thailand"""

        if self.address_country.code != "TH" and not self.passport:
            raise ValidationError("Passport number is required for foreign nationals")
        pass

    def clean(self) -> None:
        self.validate_passport()

    @override
    def save(self, *args: Any, **kwargs: Any) -> None:
        self.validate_passport()

        if self.pk:
            # Update associated Stripe customer
            stripe.Customer.modify(
                self.stripe_id,
                name=f"{self.first_name} {self.last_name}",
                email=self.user.email,
                address={
                    "city": cast(str, self.address_city),
                    "country": cast(str, self.address_country),
                    "line1": cast(str, self.address_line1),
                    "line2": cast(str, self.address_line2),
                    "postal_code": cast(str, self.address_postal_code),
                    "state": cast(str, self.address_state),
                },
                phone=self.phone,
            )
        super().save(*args, **kwargs)
