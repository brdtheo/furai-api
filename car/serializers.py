from rest_framework import serializers

from .models import Car, CarFeature, CarMedia


class CarSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()

    class Meta:
        model = Car
        fields = "__all__"


class CarMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarMedia
        fields = "__all__"


class CarFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarFeature
        fields = "__all__"
