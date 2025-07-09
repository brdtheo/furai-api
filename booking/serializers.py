from typing import Any

from django.utils import timezone
from django_countries.serializer_fields import CountryField
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from customer.models import Customer
from user.models import CustomUser

from .enums import BookingStatus
from .errors import (
    BOOKING_CAR_UNAVAILABLE_TIME_PERIOD_ERROR,
    BOOKING_CUSTOMER_PASSPORT_REQUIRED_ERROR,
    BOOKING_END_DATE_BEFORE_START_DATE_ERROR,
    BOOKING_END_DATE_IN_THE_PAST_ERROR,
    BOOKING_SAME_DAY_BOOKING_ERROR,
    BOOKING_START_DATE_IN_THE_PAST_ERROR,
)
from .models import Booking

THAILAND_COUNTRY_CODE = "TH"


class BookingSerializer(serializers.ModelSerializer, CountryFieldMixin):
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    address_line1 = serializers.CharField(write_only=True)
    address_line2 = serializers.CharField(
        required=False, write_only=True, allow_blank=True, allow_null=True
    )
    address_city = serializers.CharField(write_only=True)
    address_postal_code = serializers.CharField(write_only=True)
    address_state = serializers.CharField(
        required=False, write_only=True, allow_blank=True, allow_null=True
    )
    address_country = CountryField(write_only=True)
    phone = serializers.CharField(write_only=True)
    passport = serializers.CharField(
        required=False, write_only=True, allow_blank=True, allow_null=True
    )

    class Meta:
        model = Booking
        fields = "__all__"
        extra_kwargs = {
            "customer": {"read_only": True},
            "status": {"read_only": True},
        }

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        address_country = attrs.get("address_country")
        passport = attrs.get("passport")
        car = attrs.get("car")

        # Raise an error if one of the dates is in the past
        if start_date is not None and end_date is not None:
            if start_date < timezone.now():
                raise BOOKING_START_DATE_IN_THE_PAST_ERROR
            if end_date < timezone.now():
                raise BOOKING_END_DATE_IN_THE_PAST_ERROR

        # Raise an error if the end date is before the start date
        if end_date is not None and end_date < start_date:
            raise BOOKING_END_DATE_BEFORE_START_DATE_ERROR

        # Raise an error if start date is on the same day
        if start_date is not None and start_date.date().day == timezone.now().day:
            raise BOOKING_SAME_DAY_BOOKING_ERROR

        # Raise an error if the car is unavailable in the requested time period
        if Booking.objects.filter(
            car=car,
            start_date__lt=end_date,
            end_date__gt=start_date,
        ).exists():
            raise BOOKING_CAR_UNAVAILABLE_TIME_PERIOD_ERROR

        # Raise an error if customer is a foreign national and passport number is empty
        if address_country != THAILAND_COUNTRY_CODE and not passport:
            raise BOOKING_CUSTOMER_PASSPORT_REQUIRED_ERROR

        return attrs

    def create(self, validated_data: dict[str, Any]) -> Booking:
        # Create user and customer if not already existing
        try:
            user = CustomUser.objects.get(email=validated_data["email"])
        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create(email=validated_data["email"])
        try:
            customer = Customer.objects.get(user=user)
            # Override customer infos by request payload
            Customer.objects.filter(
                pk=customer.pk,
            ).update(
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                address_line1=validated_data["address_line1"],
                address_line2=validated_data["address_line2"],
                address_city=validated_data["address_city"],
                address_state=validated_data["address_state"],
                address_postal_code=validated_data["address_postal_code"],
                address_country=validated_data["address_country"],
                phone=validated_data["phone"],
                passport=validated_data["passport"],
            )
        except Customer.DoesNotExist:
            customer = Customer.objects.create(
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                address_line1=validated_data["address_line1"],
                address_line2=validated_data["address_line2"],
                address_city=validated_data["address_city"],
                address_state=validated_data["address_state"],
                address_postal_code=validated_data["address_postal_code"],
                address_country=validated_data["address_country"],
                phone=validated_data["phone"],
                passport=validated_data["passport"],
                user=user,
            )

        # Filter out extra fields for Booking creation
        validated_data.pop("email")
        validated_data.pop("first_name")
        validated_data.pop("last_name")
        validated_data.pop("address_line1")
        validated_data.pop("address_line2")
        validated_data.pop("address_city")
        validated_data.pop("address_state")
        validated_data.pop("address_postal_code")
        validated_data.pop("address_country")
        validated_data.pop("phone")
        validated_data.pop("passport")

        booking = Booking.objects.create(
            customer=customer, status=BookingStatus.CONFIRMED, **validated_data
        )
        return booking
