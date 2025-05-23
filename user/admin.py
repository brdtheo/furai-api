from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "is_staff",
    )
    list_editable = ("is_staff",)
    search_fields = ("email",)
    list_per_page = 30
