from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404

from .models import Car, CarFeature, CarMedia
from .serializers import CarFeatureSerializer, CarMediaSerializer, CarSerializer


def car_list(request: HttpRequest) -> JsonResponse:
    """
    List all cars
    """

    if request.method == "GET":
        car_list = Car.objects.all().order_by("price_24_hours_cents")
        serializer = CarSerializer(car_list, many=True)
        return JsonResponse(serializer.data, safe=False)

    else:
        return JsonResponse({"error": "Unknown request type"}, status=400)


def car_details(request: HttpRequest, id: int) -> JsonResponse:
    """
    Retrieve a car instance
    """

    if request.method == "GET":
        car = get_object_or_404(Car, pk=id)
        serializer = CarSerializer(car)
        return JsonResponse(serializer.data, safe=False)

    else:
        return JsonResponse({"error": "Unknown request type"}, status=400)


def car_media_list(request: HttpRequest) -> JsonResponse:
    """
    List car medias
    """

    if request.method == "GET":
        car_id = request.GET["car"] if request.GET else None
        queryset = CarMedia.objects.all()
        if car_id:
            queryset = CarMedia.objects.filter(car_id=car_id)
        serializer = CarMediaSerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)

    else:
        return JsonResponse({"error": "Unknown request type"}, status=400)


def car_feature_list(request: HttpRequest) -> JsonResponse:
    """
    List car features
    """

    if request.method == "GET":
        id__in = (
            request.GET["id__in"].split(",")
            if request.GET and request.GET["id__in"]
            else None
        )
        queryset = CarFeature.objects.all()
        if id__in:
            queryset = CarFeature.objects.filter(id__in=id__in)
        serializer = CarFeatureSerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)

    else:
        return JsonResponse({"error": "Unknown request type"}, status=400)
