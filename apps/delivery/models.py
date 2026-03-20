from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class DeliveryZone(models.Model):
    """Delivery zone with pricing and time estimates."""

    name = models.CharField(_("название"), max_length=255)
    description = models.TextField(_("описание"), blank=True)
    base_price = models.DecimalField(
        _("базовая цена"), max_digits=10, decimal_places=2
    )
    estimated_minutes = models.PositiveIntegerField(_("ориентировочное время (мин)"))
    is_active = models.BooleanField(_("активна"), default=True)

    class Meta:
        verbose_name = _("зона доставки")
        verbose_name_plural = _("зоны доставки")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class CourierShift(models.Model):
    """Courier work shift schedule."""

    courier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shifts",
        verbose_name=_("курьер"),
    )
    date = models.DateField(_("дата"))
    start_time = models.TimeField(_("начало смены"))
    end_time = models.TimeField(_("конец смены"))
    zone = models.ForeignKey(
        DeliveryZone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shifts",
        verbose_name=_("зона"),
    )

    class Meta:
        verbose_name = _("смена курьера")
        verbose_name_plural = _("смены курьеров")
        ordering = ["date", "start_time"]

    def __str__(self) -> str:
        return f"{self.courier} — {self.date} ({self.start_time}–{self.end_time})"
