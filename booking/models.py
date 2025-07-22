from typing import Any, Self

from django.db import models

from car.models import Car
from customer.models import Customer
from furai.models import BaseModel

from .enums import BookingStatus


class BookingManager(models.Manager):
    def create(self, **kwargs: Any) -> Any:
        from .services import BookingService

        service = BookingService(**kwargs)
        customer = service.create()
        return customer


class Booking(BaseModel):
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
    price_cents = models.IntegerField(
        help_text="The total price of the booking, in cents",
        db_comment="The total price of the booking, in cents",
    )
    status = models.CharField(
        choices=BookingStatus,
        help_text="The current booking status",
        db_comment="The current booking status",
        default=BookingStatus.UNPAID,
    )

    def __str__(self) -> str:
        return f"{self.customer.name} - {self.car.name}"

    def mark_as_cancelled(
        self,
        is_staff_origin: bool = False,
    ) -> Self:
        """Cancel a booking"""

        if is_staff_origin:
            self.status = BookingStatus.CANCELED_BY_STAFF
        else:
            self.status = BookingStatus.CANCELED_BY_CUSTOMER
        self.save()
        return self

    def mark_as_complete(self) -> Self:
        """Set a booking status as complete"""

        self.status = BookingStatus.COMPLETED
        self.save()
        return self
