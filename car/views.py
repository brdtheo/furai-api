from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from .models import Car, CarMedia
from .serializers import CarMediaSerializer, CarSerializer


@csrf_exempt
def car_list(request: HttpRequest) -> JsonResponse:
    """
    List all cars or create a new car instance
    """

    if request.method == "GET":
        car_list = Car.objects.all().order_by("price_24_hours_cents")
        serializer = CarSerializer(car_list, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == "POST":
        payload = JSONParser.parse(request)  # type: ignore
        serializer = CarSerializer(data=payload)

        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        serializer.save()
        return JsonResponse(serializer.data, status=201)

    else:
        return JsonResponse({"error": "Unknown request type"}, status=400)


@csrf_exempt
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


@csrf_exempt
def car_media_list(request: HttpRequest) -> JsonResponse:
    """
    List all car medias or create a new car media instance
    """

    if request.method == "GET":
        car_media_list = CarMedia.objects.all()
        serializer = CarMediaSerializer(car_media_list, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == "POST":
        payload = JSONParser.parse(request)  # type: ignore
        serializer = CarMediaSerializer(data=payload)

        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        serializer.save()
        return JsonResponse(serializer.data, status=201)

    else:
        return JsonResponse({"error": "Unknown request type"}, status=400)
