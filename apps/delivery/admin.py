from django.contrib import admin

from .models import CourierShift, DeliveryZone


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "base_price", "estimated_minutes", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(CourierShift)
class CourierShiftAdmin(admin.ModelAdmin):
    list_display = ("courier", "date", "start_time", "end_time", "zone")
    list_filter = ("date", "zone")
    search_fields = ("courier__username", "courier__first_name", "courier__last_name")
