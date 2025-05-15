from django.urls import URLPattern, URLResolver, path

from .views import car_list

urlpatterns: list[URLResolver | URLPattern] = [
    path("", car_list, name="car-list"),
]
