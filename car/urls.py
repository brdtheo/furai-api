from django.urls import URLPattern, URLResolver, path

from .views import CarDetail, CarFeatureList, CarList, CarMediaList

urlpatterns: list[URLResolver | URLPattern] = [
    path("cars", CarList.as_view()),
    path("cars/<int:pk>", CarDetail.as_view()),
    path("car-medias", CarMediaList.as_view()),
    path("car-features", CarFeatureList.as_view()),
]
