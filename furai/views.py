from typing import Any

from django.views.generic import TemplateView

from car.models import Car, CarMedia


class HomeView(TemplateView):
    template_name = "index.html"

    hero_buttons = [
        {"label": "our fleet", "href": "#fleet"},
        {"label": "line", "href": "#contact"},
        {"label": "whatsapp", "href": "#contact"},
    ]
    hero_thumbnail = "https://www.jcwhitney.com/wp-content/uploads/2024/08/Screenshot-at-Aug-13-13-25-42-1500x442.webp"

    def get_context_data(
        self, **kwargs: Any
    ) -> dict[str, list[dict[str, str]] | list[dict[str, str]] | str]:
        context = super().get_context_data(**kwargs)

        car_list = Car.objects.all().order_by("price_24_hours_cents")[:10]
        car_with_media_list: list[dict[str, str]] = []
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

        context["car_list"] = car_with_media_list
        context["hero_buttons"] = self.hero_buttons
        context["hero_thumbnail"] = self.hero_thumbnail
        return context
