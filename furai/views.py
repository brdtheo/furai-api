from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from car.models import Car, CarMedia


def index(request: HttpRequest) -> HttpResponse:
    car_list = Car.objects.all().order_by("price_24_hours_cents")[:10]

    car_with_media_list = []
    for car in car_list:
        car_media_thumbnail = CarMedia.objects.get(car=car, is_thumbnail=True)
        car_with_media_list.append(
            {
                "slug": car.slug,
                "name": car.name,
                "transmission": car.transmission,
                "thumbnail": car_media_thumbnail.url,
            }
        )

    return render(
        request,
        "index.html",
        context={"car_list": car_with_media_list},
    )
