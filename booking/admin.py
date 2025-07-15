from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from .models import Booking


@admin.action(description="Cancel selected bookings")
def cancel(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[Booking],
) -> None:
    for booking in queryset.all():
        booking.cancel(True)


@admin.action(description="Mark selected bookings as complete")
def mark_as_complete(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[Booking],
) -> None:
    for booking in queryset.all():
        booking.mark_as_complete()


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("customer", "car", "start_date", "end_date", "status")
    search_fields = (
        "first_name",
        "last_name",
    )
    list_filter = ("customer", "car")
    list_per_page = 30
    actions = [mark_as_complete, cancel]

    def response_change(self, request: HttpRequest, obj: Booking) -> HttpResponse:
        if "_cancel" in request.POST:
            obj.cancel(True)
            self.message_user(request, "This booking has been cancelled")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)
