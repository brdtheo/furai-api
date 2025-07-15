from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import Customer


class IsCustomerUser(IsAuthenticated):
    """
    Allow access only if authenticated user is linked to the customer
    """

    def has_object_permission(
        self, request: Request, view: APIView, obj: Customer
    ) -> bool:
        return obj.user == request.user
