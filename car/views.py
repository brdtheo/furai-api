from typing import Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from .enums import CarFeatures
from .models import Car, CarFeature, CarMedia


class CarDetailView(DetailView):
    model = Car
    template_name = "details.html"
    slug_url_kwarg = "car_slug"

    def get_context_data(
        self, **kwargs: Any
    ) -> dict[
        str,
        Car
        | QuerySet[CarMedia, CarMedia]
        | QuerySet[CarFeature, CarFeature]
        | CarFeatures
        | list[dict[str, str]]
        | CarMedia,
    ]:
        context = super().get_context_data(**kwargs)
        car = get_object_or_404(Car, slug=self.kwargs.get("car_slug"))
        car_media_list = CarMedia.objects.filter(car=car)
        car_feature_list = CarFeature.objects.filter(car=car)
        hero_buttons = [
            {"label": "book this car", "href": "#"},
            {"label": "ask a question", "href": "#"},
        ]
        hero_thumbnail = car_media_list.get(is_thumbnail=True)

        context["car"] = car
        context["car_media_list"] = car_media_list
        context["car_feature_list"] = car_feature_list
        context["all_car_features"] = CarFeatures
        context["hero_buttons"] = hero_buttons
        context["hero_thumbnail"] = hero_thumbnail
        return context
