from django_countries.serializer_fields import CountryField
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from .models import Booking


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
