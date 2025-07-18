from typing import Self

import resend
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from resend.emails._email import Email

from car.models import Car, CarMedia
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
    created_at = models.DateTimeField(
        help_text="The creation date of the booking",
        db_comment="The creation date of the booking",
        default=timezone.now,
    )

    def __str__(self) -> str:
        return f"{self.customer.name} - {self.car.name}"

    def send_confirmation_email(self) -> Email:
        """Send an email to the user when a new Booking is created"""

        queryset = CarMedia.objects.filter(car=self.car, is_thumbnail=True)
        car_thumbnail = queryset[0].url if queryset.exists() else None
        html_body = render_to_string(
            "booking-confirmation.html",
            {
                "start_date": self.start_date,
                "end_date": self.end_date,
                "car_thumbnail": car_thumbnail,
                "car_name": self.car.name,
                "status": self.status,
            },
        )
        params: resend.Emails.SendParams = {
            "from": "Furai car rental <noreply@furai-jdm.com>",
            "to": [self.customer.user.email],
            "subject": "Your booking confirmation",
            "html": html_body,
        }
        return resend.Emails.send(params)

    def send_cancellation_email(self) -> Email:
        """Send an email to the user when a Booking is cancelled"""

        queryset = CarMedia.objects.filter(car=self.car, is_thumbnail=True)
        car_thumbnail = queryset[0].url if queryset.exists() else None
        html_body = render_to_string(
            "booking-cancellation.html",
            {
                "start_date": self.start_date,
                "end_date": self.end_date,
                "car_thumbnail": car_thumbnail,
                "car_name": self.car.name,
                "status": self.status,
            },
        )
        params: resend.Emails.SendParams = {
            "from": "Furai car rental <noreply@furai-jdm.com>",
            "to": [self.customer.user.email],
            "subject": "Your booking has been cancelled",
            "html": html_body,
        }
        return resend.Emails.send(params)

    def cancel(
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
