from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def car_list(request: HttpRequest) -> HttpResponse:
    return render(request,"list.html")
