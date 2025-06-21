from django.urls import path

from .views import CustomerDetail

urlpatterns = [
    path("customers/<int:pk>", CustomerDetail.as_view(), name="customer-detail")
]
