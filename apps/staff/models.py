from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    """User role choices."""

    ADMIN = "admin", _("Администратор")
    MANAGER = "manager", _("Менеджер")
    FLORIST = "florist", _("Флорист")
    COURIER = "courier", _("Курьер")


class User(AbstractUser):
    """Custom user model with role and contact fields."""

    role = models.CharField(
        _("роль"),
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.MANAGER,
    )
    phone = models.CharField(_("телефон"), max_length=20, blank=True)
    telegram_id = models.CharField(_("Telegram ID"), max_length=100, blank=True)

    class Meta:
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")
        ordering = ["username"]

    def __str__(self) -> str:
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
