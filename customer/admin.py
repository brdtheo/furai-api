from django.contrib import admin

from booking.models import Booking

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "address_country", "booking_count")
    search_fields = (
        "first_name",
        "last_name",
    )
    readonly_fields = ("stripe_id",)
    list_filter = ("address_country",)
    list_per_page = 30

    @admin.display(description="Name")
    def name(self, obj: Customer) -> str:
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description="Booking count")
    def booking_count(self, obj: Customer) -> int:
        return Booking.objects.filter(customer=obj).count()
