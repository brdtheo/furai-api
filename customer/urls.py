from django.urls import path

from .views import CustomerMe

urlpatterns = [
    path("customers/me", CustomerMe.as_view(), name="customer-me"),
]
