from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "full_name", "role", "phone", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (
        (_("Дополнительно"), {"fields": ("role", "phone", "telegram_id")}),
    )

    @admin.display(description=_("ФИО"))
    def full_name(self, obj):
        return obj.get_full_name() or obj.username
