from django.urls import URLPattern, URLResolver, path

from .views import CarDetailView

urlpatterns: list[URLResolver | URLPattern] = [
    path("<str:car_slug>", CarDetailView.as_view(), name="car-details"),
]
