from django.contrib import admin
from django.db.models.query import QuerySet

from .enums import BookingStatus
from .models import Booking


@admin.action(description="Mark bookings as complete")
def mark_as_complete(modeladmin, request, queryset: QuerySet[Booking]):
    queryset.update(status=BookingStatus.COMPLETED)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("customer", "car", "start_date", "end_date", "status")
    search_fields = (
        "first_name",
        "last_name",
    )
    list_filter = ("customer", "car")
    list_per_page = 30
    actions = [mark_as_complete]
