from django.urls import URLPattern, URLResolver, path

from .views import car_details

urlpatterns: list[URLResolver | URLPattern] = [
    path("<str:car_slug>", car_details, name="car-details"),
]
