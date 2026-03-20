from django.contrib import admin

from .models import (
    BouquetComponent,
    BouquetRecipe,
    Flower,
    FlowerBatch,
    Supplier,
    WriteOff,
)


@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "default_unit")
    list_filter = ("category",)
    search_fields = ("name",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_phone", "email")
    search_fields = ("name", "email")


class BouquetComponentInline(admin.TabularInline):
    model = BouquetComponent
    extra = 1


@admin.register(FlowerBatch)
class FlowerBatchAdmin(admin.ModelAdmin):
    list_display = (
        "flower",
        "supplier",
        "arrival_date",
        "expiry_date",
        "quantity",
        "unit_price",
        "status",
    )
    list_filter = ("status", "flower", "supplier")
    search_fields = ("flower__name", "supplier__name")
    readonly_fields = ("created_at",)


@admin.register(BouquetRecipe)
class BouquetRecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "packaging", "labor_cost", "margin_percent", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    inlines = [BouquetComponentInline]


@admin.register(WriteOff)
class WriteOffAdmin(admin.ModelAdmin):
    list_display = ("batch", "quantity", "reason", "performed_by", "created_at")
    list_filter = ("reason", "created_at")
    readonly_fields = ("created_at",)
