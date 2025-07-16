from django.contrib import admin

from .models import Car, CarFeature, CarMedia


@admin.display(ordering="slug")
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "price_hourly_cents",
        "price_three_hours_cents",
        "price_six_hours_cents",
        "price_nine_hours_cents",
        "price_twelve_hours_cents",
        "price_twenty_four_hours_cents",
    )
    list_editable = (
        "price_hourly_cents",
        "price_three_hours_cents",
        "price_six_hours_cents",
        "price_nine_hours_cents",
        "price_twelve_hours_cents",
        "price_twenty_four_hours_cents",
    )
    search_fields = (
        "make",
        "model",
    )
    list_filter = ("transmission", "drivetrain", "fuel_type", "features")
    filter_horizontal = ("features",)
    list_per_page = 5


@admin.register(CarFeature)
class CarFeatureAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")


@admin.register(CarMedia)
class CarMediaAdmin(admin.ModelAdmin):
    list_display = ("car", "url", "is_thumbnail")
    list_editable = ("is_thumbnail",)
    list_filter = ("car",)
    list_per_page = 30
