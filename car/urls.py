from django.urls import URLPattern, URLResolver, path

from .views import car_details, car_feature_list, car_list, car_media_list

urlpatterns: list[URLResolver | URLPattern] = [
    path("cars/", car_list),
    path("cars/<int:id>/", car_details),
    path("car-medias/", car_media_list),
    path("car-features/", car_feature_list),
]
