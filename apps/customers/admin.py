from django.contrib import admin
from django.db.models import Count

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "phone",
        "email",
        "segment",
        "bonus_balance",
        "order_count",
        "created_at",
    )
    list_filter = ("segment", "created_at")
    search_fields = ("full_name", "phone", "email")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_order_count=Count("orders"))

    @admin.display(description="Заказов", ordering="_order_count")
    def order_count(self, obj):
        return obj._order_count
