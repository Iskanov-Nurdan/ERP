from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Warehouse(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Material(TimeStampedModel):
    class Unit(models.TextChoices):
        KG = "kg", "кг"
        G = "g", "г"

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64, unique=True)
    unit = models.CharField(max_length=8, choices=Unit.choices, default=Unit.KG)

    price_per_kg = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    supplier = models.CharField(max_length=255, blank=True, default="")
    min_stock = models.DecimalField(max_digits=12, decimal_places=3, default=0)

    class Meta:
        verbose_name = "Сырьё/материал"
        verbose_name_plural = "Сырьё/материалы"
        ordering = ["name"]
        indexes = [models.Index(fields=["name"]), models.Index(fields=["code"])]

    def __str__(self):
        return f"{self.name} ({self.code})"


class MaterialStock(TimeStampedModel):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="stocks")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stocks")

    quantity = models.DecimalField("Остаток", max_digits=12, decimal_places=3, default=0)

    class Meta:
        verbose_name = "Остаток сырья"
        verbose_name_plural = "Остатки сырья"
        unique_together = [("material", "warehouse")]
        ordering = ["warehouse__name", "material__name"]

    def __str__(self):
        return f"{self.warehouse}: {self.material} = {self.quantity}"


class MaterialMovement(TimeStampedModel):
    class Type(models.TextChoices):
        IN = "in", "Приход"
        OUT = "out", "Расход"
        TRANSFER = "transfer", "Перемещение"
        ADJUSTMENT = "adjustment", "Корректировка"

    movement_type = models.CharField(max_length=16, choices=Type.choices)

    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="movements")

    from_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name="movements_out"
    )
    to_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name="movements_in"
    )

    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    notes = models.TextField(blank=True, default="")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="material_movements"
    )

    class Meta:
        verbose_name = "Движение сырья"
        verbose_name_plural = "Движения сырья"
        ordering = ["-created_at"]


class MaterialReservation(TimeStampedModel):
    """Резерв сырья под производственный заказ (пока без авто-списания по рецептуре)."""
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="reservations")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="reservations")

    production_order_id = models.IntegerField()  # MVP: просто id заказа (без FK, чтоб не тянуть связи)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="material_reservations"
    )

    class Meta:
        verbose_name = "Резерв сырья"
        verbose_name_plural = "Резервы сырья"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["production_order_id"])]
