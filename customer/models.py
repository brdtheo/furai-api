from typing import Any, override

from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django_countries.fields import CountryField

from user.models import CustomUser


class Customer(models.Model):
    """Representation of a Customer"""

    stripe_id = models.CharField(
        help_text="The Stripe customer identifier linked to the customer",
        db_comment="The Stripe customer identifier linked to the customer",
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
        super().save(*args, **kwargs)
