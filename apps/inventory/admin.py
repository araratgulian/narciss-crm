from django.contrib import admin

from .models import (
    BouquetComponent,
    BouquetRecipe,
    Flower,
    FlowerBatch,
    Supplier,
    WriteOff,
)


@admin.register(FlowerBatch)
class FlowerBatchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "flower",
        "supplier",
        "arrival_date",
        "expiry_date",
        "quantity",
        "unit_price",
        "status",
        "is_expiring_soon",
    )
    list_filter = ("status", "flower", "supplier", "arrival_date")
    search_fields = ("flower__name", "supplier__name")
    date_hierarchy = "arrival_date"

    @admin.display(boolean=True, description="Горящие?")
    def is_expiring_soon(self, obj):
        from datetime import date, timedelta

        return (
            obj.expiry_date <= date.today() + timedelta(days=2)
            and obj.status == "available"
        )


class BouquetComponentInline(admin.TabularInline):
    model = BouquetComponent
    extra = 1


@admin.register(BouquetRecipe)
class BouquetRecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "packaging",
        "labor_cost",
        "margin_percent",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("name",)
    inlines = [BouquetComponentInline]


@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "default_unit")
    search_fields = ("name",)
    list_filter = ("category",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "contact_phone", "email")
    search_fields = ("name",)


@admin.register(WriteOff)
class WriteOffAdmin(admin.ModelAdmin):
    list_display = ("id", "batch", "quantity", "reason", "performed_by", "created_at")
    list_filter = ("reason", "created_at")
    search_fields = ("batch__flower__name",)
    date_hierarchy = "created_at"
