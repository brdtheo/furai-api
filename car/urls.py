from django.urls import URLPattern, URLResolver, path

from .views import car_details, car_list

urlpatterns: list[URLResolver | URLPattern] = [
    path("", car_list, name="car-list"),
    path("<str:car_slug>", car_details, name="car-details"),
]
