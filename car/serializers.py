from rest_framework import serializers

from .models import Car, CarMedia


class CarSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()

    class Meta:
        model = Car
        fields = "__all__"


class CarMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarMedia
        fields = "__all__"
