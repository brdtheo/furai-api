from django.urls import URLPattern, URLResolver, path

from .views import car_list, car_media_list

urlpatterns: list[URLResolver | URLPattern] = [
    path("cars/", car_list),
    path("car-medias/", car_media_list),
]
