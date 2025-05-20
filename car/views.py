from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from .enums import CarFeatures
from .models import Car, CarFeature, CarMedia


def car_details(request: HttpRequest, car_slug: str) -> HttpResponse:
    car = get_object_or_404(Car, slug=car_slug)
    car_media_list = CarMedia.objects.filter(car=car)
    car_feature_list = CarFeature.objects.filter(car=car)
    hero_buttons = [
        {"label": "book this car", "href": "#"},
        {"label": "ask a question", "href": "#"},
    ]
    hero_thumbnail = car_media_list.get(is_thumbnail=True)

    return render(
        request,
        "details.html",
        context={
            "car": car,
            "car_media_list": car_media_list,
            "car_feature_list": car_feature_list,
            "all_car_features": CarFeatures,
            "hero_buttons": hero_buttons,
            "hero_thumbnail": hero_thumbnail,
        },
    )
