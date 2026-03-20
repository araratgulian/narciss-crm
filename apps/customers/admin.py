from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "phone",
        "email",
        "segment",
        "bonus_balance",
        "created_at",
    )
    list_filter = ("segment", "created_at")
    search_fields = ("full_name", "phone", "email")
    readonly_fields = ("created_at", "updated_at")
