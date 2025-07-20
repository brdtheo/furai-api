from rest_framework.serializers import ModelSerializer

from .models import Customer


class CustomerSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "address_line1",
            "address_line2",
            "address_city",
            "address_postal_code",
            "address_state",
            "address_country",
            "phone",
            "passport",
            "created_at",
            "user",
        ]
