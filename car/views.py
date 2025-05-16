from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def car_details(request: HttpRequest, car_slug: str) -> HttpResponse:
    car_name = "Honda Civic 1.6 Vti"
    return render(request, "details.html", context={"car_name": car_name})
