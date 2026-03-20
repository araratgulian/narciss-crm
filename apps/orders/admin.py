from django.contrib import admin

from .models import Order, OrderItem, OrderStatusLog


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class OrderStatusLogInline(admin.TabularInline):
    model = OrderStatusLog
    extra = 0
    readonly_fields = ("old_status", "new_status", "changed_by", "changed_at")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "customer",
        "status",
        "delivery_date",
        "delivery_time_slot",
        "total_price",
        "payment_status",
        "source",
        "created_at",
    )
    list_filter = ("status", "payment_status", "source", "delivery_date")
    search_fields = ("customer__full_name", "customer__phone", "delivery_address")
    readonly_fields = ("created_at", "updated_at")
    inlines = [OrderItemInline, OrderStatusLogInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "bouquet_recipe", "quantity", "unit_price")
    list_filter = ("order__status",)


@admin.register(OrderStatusLog)
class OrderStatusLogAdmin(admin.ModelAdmin):
    list_display = ("order", "old_status", "new_status", "changed_by", "changed_at")
    list_filter = ("new_status",)
    readonly_fields = ("order", "old_status", "new_status", "changed_by", "changed_at")
