from django.contrib import admin

from .models import Car, CarFeature, CarMedia


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price_one_hour",
        "price_three_hours",
        "price_six_hours",
        "price_nine_hours",
        "price_twenty_four_hours",
    )
    search_fields = (
        "make",
        "model",
    )
    readonly_fields = ("slug",)
    list_filter = ("transmission", "drivetrain", "fuel_type", "features")
    filter_horizontal = ("features",)
    list_per_page = 10

    @admin.display(description="Price - 1 hour")
    def price_one_hour(self, obj: Car) -> str:
        return f"{int(obj.price_hourly_cents / 100)} THB"

    @admin.display(description="Price - 3 hour")
    def price_three_hours(self, obj: Car) -> str:
        return f"{int(obj.price_three_hours_cents / 100)} THB"

    @admin.display(description="Price - 6 hour")
    def price_six_hours(self, obj: Car) -> str:
        return f"{int(obj.price_six_hours_cents / 100)} THB"

    @admin.display(description="Price - 9 hour")
    def price_nine_hours(self, obj: Car) -> str:
        return f"{int(obj.price_nine_hours_cents / 100)} THB"

    @admin.display(description="Price - 24 hour")
    def price_twenty_four_hours(self, obj: Car) -> str:
        return f"{int(obj.price_twenty_four_hours_cents / 100)} THB"


@admin.register(CarFeature)
class CarFeatureAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")


@admin.register(CarMedia)
class CarMediaAdmin(admin.ModelAdmin):
    list_display = ("car", "url", "is_thumbnail")
    list_editable = ("is_thumbnail",)
    list_filter = ("car",)
    list_per_page = 30
