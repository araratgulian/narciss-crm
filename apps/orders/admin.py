from django.contrib import admin

from .models import Order, OrderItem, OrderStatusLog


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("unit_price",)


class OrderStatusLogInline(admin.TabularInline):
    model = OrderStatusLog
    extra = 0
    readonly_fields = (
        "old_status",
        "new_status",
        "changed_by",
        "changed_at",
        "comment",
    )
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "status",
        "delivery_date",
        "delivery_time_slot",
        "total_price",
        "payment_status",
        "source",
        "created_at",
    )
    list_filter = (
        "status",
        "payment_status",
        "source",
        "delivery_date",
        "delivery_time_slot",
    )
    search_fields = (
        "customer__full_name",
        "customer__phone",
        "delivery_address",
        "notes",
    )
    list_editable = ("status",)
    date_hierarchy = "created_at"
    inlines = [OrderItemInline, OrderStatusLogInline]
    raw_id_fields = ("customer", "assigned_florist", "assigned_courier")

    actions = ["mark_as_paid"]

    @admin.action(description="Отметить как оплаченные")
    def mark_as_paid(self, request, queryset):
        updated = queryset.filter(status="new").update(
            status="paid", payment_status="paid"
        )
        self.message_user(request, f"Обновлено заказов: {updated}")
