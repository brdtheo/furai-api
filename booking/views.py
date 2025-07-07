from typing import cast

from django.db.models.query import QuerySet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from user.models import CustomUser

from .models import Booking
from .serializers import BookingSerializer


class BookingList(ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Booking]:
        user: CustomUser = cast(
            CustomUser,
            self.request.user,
        )
        queryset = Booking.objects.filter(customer__user=user).order_by("-created_at")
        return queryset
