from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class OrderStatus(models.TextChoices):
    """Order status choices."""

    NEW = "new", _("Новый")
    PAID = "paid", _("Оплачен")
    ASSEMBLING = "assembling", _("Сборка")
    ASSEMBLED = "assembled", _("Собран")
    DELIVERING = "delivering", _("Доставка")
    DELIVERED = "delivered", _("Доставлен")
    COMPLETED = "completed", _("Завершён")
    CANCELLED = "cancelled", _("Отменён")
    REFUNDED = "refunded", _("Возврат")


class TimeSlot(models.TextChoices):
    """Delivery time slot choices."""

    SLOT_09_12 = "09-12", _("09:00–12:00")
    SLOT_12_15 = "12-15", _("12:00–15:00")
    SLOT_15_18 = "15-18", _("15:00–18:00")
    SLOT_18_21 = "18-21", _("18:00–21:00")


class PaymentStatus(models.TextChoices):
    """Payment status choices."""

    PENDING = "pending", _("Ожидает")
    PAID = "paid", _("Оплачено")
    REFUNDED = "refunded", _("Возвращено")


class OrderSource(models.TextChoices):
    """Order source choices."""

    WEBSITE = "website", _("Сайт")
    WHATSAPP = "whatsapp", _("WhatsApp")
    TELEGRAM = "telegram", _("Telegram")
    PHONE = "phone", _("Телефон")
    INSTAGRAM = "instagram", _("Instagram")


class Order(models.Model):
    """Customer order with delivery details and status tracking."""

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name=_("клиент"),
    )
    status = models.CharField(
        _("статус"),
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
    )
    delivery_date = models.DateField(_("дата доставки"))
    delivery_time_slot = models.CharField(
        _("время доставки"), max_length=20, choices=TimeSlot.choices
    )
    delivery_address = models.TextField(_("адрес доставки"))
    delivery_zone = models.ForeignKey(
        "delivery.DeliveryZone",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name=_("зона доставки"),
    )
    total_price = models.DecimalField(
        _("итоговая цена"), max_digits=10, decimal_places=2
    )
    payment_status = models.CharField(
        _("статус оплаты"),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    assigned_florist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="florist_orders",
        verbose_name=_("флорист"),
    )
    assigned_courier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courier_orders",
        verbose_name=_("курьер"),
    )
    photo_before_delivery = models.ImageField(
        _("фото перед доставкой"), upload_to="deliveries/", blank=True
    )
    notes = models.TextField(_("заметки"), blank=True)
    source = models.CharField(
        _("источник"),
        max_length=20,
        choices=OrderSource.choices,
        default=OrderSource.WEBSITE,
    )
    created_at = models.DateTimeField(_("создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("обновлено"), auto_now=True)

    class Meta:
        verbose_name = _("заказ")
        verbose_name_plural = _("заказы")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Заказ #{self.pk} — {self.customer} ({self.get_status_display()})"


class OrderItem(models.Model):
    """Line item in an order linking to a bouquet recipe."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("заказ"),
    )
    bouquet_recipe = models.ForeignKey(
        "inventory.BouquetRecipe",
        on_delete=models.PROTECT,
        verbose_name=_("техкарта букета"),
    )
    quantity = models.PositiveIntegerField(_("количество"), default=1)
    unit_price = models.DecimalField(
        _("цена за единицу"), max_digits=10, decimal_places=2
    )

    class Meta:
        verbose_name = _("позиция заказа")
        verbose_name_plural = _("позиции заказа")
        ordering = ["pk"]

    def __str__(self) -> str:
        return f"{self.bouquet_recipe} x{self.quantity}"


class OrderStatusLog(models.Model):
    """Audit log for order status transitions."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_logs",
        verbose_name=_("заказ"),
    )
    old_status = models.CharField(_("старый статус"), max_length=20)
    new_status = models.CharField(_("новый статус"), max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("изменил"),
    )
    changed_at = models.DateTimeField(_("время изменения"), auto_now_add=True)
    comment = models.TextField(_("комментарий"), blank=True)

    class Meta:
        verbose_name = _("лог статуса заказа")
        verbose_name_plural = _("логи статусов заказов")
        ordering = ["-changed_at"]

    def __str__(self) -> str:
        return f"Заказ #{self.order_id}: {self.old_status} → {self.new_status}"
