from typing import Any, override

from django.db import models
from django.forms import ValidationError
from django.utils import timezone

from car.models import Car
from customer.models import Customer

from .enums import BookingStatus


class Booking(models.Model):
    """Representation of a Booking"""

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        help_text="The car linked to the booking",
        db_comment="The car linked to the booking",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        help_text="The customer linked to the booking",
        db_comment="The customer linked to the booking",
    )
    start_date = models.DateTimeField(
        help_text="The start date of the booking",
        db_comment="The start date of the booking",
    )
    end_date = models.DateTimeField(
        help_text="The end date of the booking",
        db_comment="The end date of the booking",
    )
    status = models.CharField(
        choices=BookingStatus,
        help_text="The current booking status",
        db_comment="The current booking status",
    )
    created_at = models.DateTimeField(
        help_text="The creation date of the booking",
        db_comment="The creation date of the booking",
        default=timezone.now,
    )

    def __str__(self) -> str:
        return f"{self.customer.name} - {self.car.name}"

    @override
    def save(self, *args: Any, **kwargs: Any) -> None:
        # Raise an error if the start date is in the past
        if self.start_date < timezone.now():
            raise ValidationError("Cannot create a booking with start_date in the past")

        # Raise an error if the start date is on the same day
        if self.start_date.date().day == timezone.now().day:
            raise ValidationError("Cannot create a booking on the same day")

        super().save(*args, **kwargs)
