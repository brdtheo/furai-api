from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.generics import RetrieveAPIView

from .models import Customer
from .serializers import CustomerSerializer


class CustomerDetail(RetrieveAPIView):
    """
    Retrieve a customer instance
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class CustomerMe(RetrieveAPIView):
    """
    Retrieve the customer instance from current authenticated user
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> Customer:
        return get_object_or_404(Customer, user=self.request.user)
