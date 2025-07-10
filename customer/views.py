from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Customer
from .permissions import IsCustomerUser
from .serializers import CustomerSerializer


class CustomerMe(RetrieveAPIView):
    """
    Retrieve the customer instance from current authenticated user
    """

    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> Customer:
        return get_object_or_404(Customer, user=self.request.user)


class CustomerDetailView(UpdateAPIView):
    """
    Update a given customer instance
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsCustomerUser]
