from typing import Any

from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Booking
from .serializers import BookingSerializer


class BookingList(ListAPIView):
    queryset = Booking.objects.order_by("-created_at")
    serializer_class = BookingSerializer

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        customer_id = request.GET["customer"] if request.GET else None
        if customer_id:
            self.queryset = Booking.objects.filter(customer_id=customer_id).order_by("-created_at")
        return self.list(request, *args, **kwargs)
