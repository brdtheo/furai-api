from rest_framework.generics import RetrieveAPIView

from .models import Customer
from .serializers import CustomerSerializer


class CustomerDetail(RetrieveAPIView):
    """
    Retrieve a customer instance
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
