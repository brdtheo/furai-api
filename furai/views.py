from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from car.models import Car, CarMedia


def index(request: HttpRequest) -> HttpResponse:
    hero_buttons = [
        {"label": "our fleet", "href": "#fleet"},
        {"label": "line", "href": "#contact"},
        {"label": "whatsapp", "href": "#contact"},
    ]
    hero_thumbnail = "https://www.jcwhitney.com/wp-content/uploads/2024/08/Screenshot-at-Aug-13-13-25-42-1500x442.webp"

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
        context={
            "car_list": car_with_media_list,
            "hero_buttons": hero_buttons,
            "hero_thumbnail": hero_thumbnail,
        },
    )
