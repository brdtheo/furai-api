from django.urls import path

from .views import CustomerDetailView, CustomerMe

urlpatterns = [
    path("customers/<int:pk>", CustomerDetailView.as_view(), name="customer-detail"),
    path("customers/me", CustomerMe.as_view(), name="customer-me"),
]
