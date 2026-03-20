from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomerSegment(models.TextChoices):
    """Customer segment choices."""

    NEW = "new", _("Новый")
    REGULAR = "regular", _("Постоянный")
    VIP = "vip", _("VIP")
    CHURNED = "churned", _("Отток")


class Customer(models.Model):
    """Customer profile with contact info, preferences, and bonus balance."""

    phone = models.CharField(_("телефон"), max_length=20, unique=True, db_index=True)
    email = models.EmailField(_("email"), blank=True)
    full_name = models.CharField(_("ФИО"), max_length=255)
    all_channels = models.JSONField(
        _("каналы связи"),
        default=dict,
        help_text=_("telegram, whatsapp, instagram handles"),
    )
    preferences = models.JSONField(
        _("предпочтения"),
        default=dict,
        help_text=_("allergies, fav_flowers, color_palette"),
    )
    memorable_dates = models.JSONField(
        _("памятные даты"),
        default=list,
        help_text=_("[{date, description, reminder_days_before}]"),
    )
    segment = models.CharField(
        _("сегмент"),
        max_length=20,
        choices=CustomerSegment.choices,
        default=CustomerSegment.NEW,
    )
    bonus_balance = models.DecimalField(
        _("бонусный баланс"), max_digits=10, decimal_places=2, default=0
    )
    notes = models.TextField(_("заметки"), blank=True)
    created_at = models.DateTimeField(_("создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("клиент")
        verbose_name_plural = _("клиенты")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.phone})"
