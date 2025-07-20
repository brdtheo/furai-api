import json

from django.db.models.query import QuerySet
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from .models import Car, CarFeature, CarMedia
from .serializers import CarFeatureSerializer, CarMediaSerializer, CarSerializer


class CarViewSet(ReadOnlyModelViewSet):
    """
    List or retrieve cars
    """

    queryset = Car.objects.order_by("price_twenty_four_hours_cents")
    serializer_class = CarSerializer


class CarMediaViewSet(ListModelMixin, GenericViewSet):
    """
    List car medias
    """

    serializer_class = CarMediaSerializer

    def get_queryset(self) -> QuerySet[CarMedia]:
        queryset = CarMedia.objects.order_by("created_at")
        car_id = self.request.query_params.get("car")
        is_thumbnail = self.request.query_params.get("is_thumbnail")
        if car_id is not None:
            queryset = queryset.filter(car_id=car_id)
        if is_thumbnail is not None:
            queryset = queryset.filter(is_thumbnail=json.loads(is_thumbnail))
        return queryset


class CarFeatureViewSet(ListModelMixin, GenericViewSet):
    """
    List car features
    """

    serializer_class = CarFeatureSerializer

    def get_queryset(self) -> QuerySet[CarFeature]:
        queryset = CarFeature.objects.order_by("created_at")
        id__in = self.request.query_params.get("id__in")
        if id__in is not None:
            queryset = queryset.filter(id__in=id__in.split(","))
        return queryset
