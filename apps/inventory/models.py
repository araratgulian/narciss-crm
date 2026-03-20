from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class BatchStatus(models.TextChoices):
    """Flower batch status choices."""

    AVAILABLE = "available", _("В наличии")
    LOW_STOCK = "low_stock", _("Мало")
    EXPIRED = "expired", _("Истёк срок")
    DEPLETED = "depleted", _("Израсходовано")


class WriteOffReason(models.TextChoices):
    """Write-off reason choices."""

    WILTED = "wilted", _("Увяли")
    DAMAGED = "damaged", _("Повреждены")
    DEFECTIVE = "defective", _("Брак")
    EXPIRED = "expired", _("Истёк срок")
    OTHER = "other", _("Другое")


class Flower(models.Model):
    """Flower type reference."""

    name = models.CharField(_("название"), max_length=255)
    category = models.CharField(_("категория"), max_length=100)
    default_unit = models.CharField(_("единица измерения"), max_length=20, default="stem")

    class Meta:
        verbose_name = _("цветок")
        verbose_name_plural = _("цветы")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Supplier(models.Model):
    """Flower supplier."""

    name = models.CharField(_("название"), max_length=255)
    contact_phone = models.CharField(_("телефон"), max_length=20, blank=True)
    email = models.EmailField(_("email"), blank=True)

    class Meta:
        verbose_name = _("поставщик")
        verbose_name_plural = _("поставщики")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class FlowerBatch(models.Model):
    """Batch of flowers from a supplier, tracked with FIFO."""

    flower = models.ForeignKey(
        Flower,
        on_delete=models.PROTECT,
        related_name="batches",
        verbose_name=_("цветок"),
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="batches",
        verbose_name=_("поставщик"),
    )
    arrival_date = models.DateField(_("дата поступления"))
    expiry_date = models.DateField(_("срок годности"))
    quantity = models.PositiveIntegerField(_("количество"))
    unit_price = models.DecimalField(
        _("цена за единицу"), max_digits=10, decimal_places=2
    )
    status = models.CharField(
        _("статус"),
        max_length=20,
        choices=BatchStatus.choices,
        default=BatchStatus.AVAILABLE,
    )
    created_at = models.DateTimeField(_("создано"), auto_now_add=True)

    class Meta:
        verbose_name = _("партия цветов")
        verbose_name_plural = _("партии цветов")
        ordering = ["arrival_date"]  # FIFO

    def __str__(self) -> str:
        return f"{self.flower} — {self.arrival_date} ({self.quantity} шт.)"


class BouquetRecipe(models.Model):
    """Bouquet recipe (tech card) with components and pricing."""

    name = models.CharField(_("название"), max_length=255)
    description = models.TextField(_("описание"), blank=True)
    components = models.ManyToManyField(
        Flower,
        through="BouquetComponent",
        verbose_name=_("компоненты"),
    )
    packaging = models.CharField(_("упаковка"), max_length=255, blank=True)
    labor_cost = models.DecimalField(
        _("стоимость работы"), max_digits=10, decimal_places=2, default=0
    )
    margin_percent = models.DecimalField(
        _("наценка (%)"), max_digits=5, decimal_places=2, default=30
    )
    is_active = models.BooleanField(_("активный"), default=True)
    image = models.ImageField(_("изображение"), upload_to="bouquets/", blank=True)

    class Meta:
        verbose_name = _("техкарта букета")
        verbose_name_plural = _("техкарты букетов")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class BouquetComponent(models.Model):
    """Component of a bouquet recipe linking flower and quantity."""

    recipe = models.ForeignKey(
        BouquetRecipe,
        on_delete=models.CASCADE,
        related_name="recipe_components",
        verbose_name=_("техкарта"),
    )
    flower = models.ForeignKey(
        Flower,
        on_delete=models.PROTECT,
        verbose_name=_("цветок"),
    )
    quantity = models.PositiveIntegerField(_("количество"))
    unit = models.CharField(_("единица измерения"), max_length=20, default="stem")

    class Meta:
        verbose_name = _("компонент букета")
        verbose_name_plural = _("компоненты букета")
        ordering = ["pk"]

    def __str__(self) -> str:
        return f"{self.flower} x{self.quantity} ({self.unit})"


class WriteOff(models.Model):
    """Write-off record for damaged/expired flowers."""

    batch = models.ForeignKey(
        FlowerBatch,
        on_delete=models.CASCADE,
        related_name="write_offs",
        verbose_name=_("партия"),
    )
    quantity = models.PositiveIntegerField(_("количество"))
    reason = models.CharField(
        _("причина"),
        max_length=20,
        choices=WriteOffReason.choices,
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("выполнил"),
    )
    created_at = models.DateTimeField(_("создано"), auto_now_add=True)
    notes = models.TextField(_("заметки"), blank=True)

    class Meta:
        verbose_name = _("списание")
        verbose_name_plural = _("списания")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Списание: {self.batch.flower} x{self.quantity} ({self.get_reason_display()})"
