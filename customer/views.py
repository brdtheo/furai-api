from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import GenericViewSet

from .models import Customer
from .permissions import IsCustomerUser
from .serializers import CustomerSerializer


class CustomerViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    """
    Retrieve or update a customer instance
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsCustomerUser]

    @action(detail=False)
    def me(self, request: Request, *args: str, **kwargs: str) -> Response:
        """Retrieve the customer instance from current authenticated user"""

        customer = get_object_or_404(Customer, user=self.request.user)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=HTTP_200_OK)
