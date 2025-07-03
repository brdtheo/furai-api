from django.urls import path

from .views import CustomerDetail, CustomerMe

urlpatterns = [
    path("customers/<int:pk>", CustomerDetail.as_view(), name="customer-detail"),
    path("customers/me", CustomerMe.as_view(), name="customer-me"),
]
