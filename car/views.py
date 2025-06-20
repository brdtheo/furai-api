from typing import Any

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Car, CarFeature, CarMedia
from .serializers import CarFeatureSerializer, CarMediaSerializer, CarSerializer


class CarList(ListAPIView, RetrieveAPIView):
    """
    List cars
    """

    queryset = Car.objects.order_by("price_24_hours_cents")
    serializer_class = CarSerializer


class CarDetail(RetrieveAPIView):
    """
    Retrieve a car instance
    """

    queryset = Car.objects.all()
    serializer_class = CarSerializer


class CarMediaList(ListAPIView):
    """
    List car medias
    """

    queryset = CarMedia.objects.all()
    serializer_class = CarMediaSerializer

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        car_id = request.GET["car"] if request.GET else None
        if car_id:
            self.queryset = CarMedia.objects.filter(car_id=car_id)
        return self.list(request, *args, **kwargs)


class CarFeatureList(ListAPIView):
    """
    List car features
    """

    queryset = CarFeature.objects.all()
    serializer_class = CarFeatureSerializer

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        id__in = (
            request.GET["id__in"].split(",")
            if request.GET and request.GET["id__in"]
            else None
        )
        if id__in:
            self.queryset = CarFeature.objects.filter(id__in=id__in)
        return self.list(request, *args, **kwargs)
