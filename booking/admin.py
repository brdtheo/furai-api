from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("customer", "car", "start_date", "end_date", "status")
    search_fields = (
        "first_name",
        "last_name",
    )
    list_filter = ("customer", "car")
    list_per_page = 30
