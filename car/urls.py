from django.urls import URLPattern, URLResolver, path

from .views import CarDetail, CarFeatureList, CarList, CarMediaList

urlpatterns: list[URLResolver | URLPattern] = [
    path("cars", CarList.as_view(), name="car-list"),
    path("cars/<int:pk>", CarDetail.as_view(), name="car-detail"),
    path("car-medias", CarMediaList.as_view(), name="car-media-list"),
    path("car-features", CarFeatureList.as_view(), name="car-feature-list"),
]
