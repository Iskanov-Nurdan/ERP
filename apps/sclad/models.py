from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RawMaterial(TimeStampedModel):
    class MaterialTypes(models.TextChoices):
        GRANULES = "granules", "Гранулы"
        COLOR = "color", "Краситель"
        ADDITIVE = "additive", "Добавка"
        PACKAGE = "package", "Упаковка"
        OTHER = "other", "Другое"

    class Units(models.TextChoices):
        KG = "kg", "кг"
        TON = "t", "т"
        LITER = "l", "л"
        PCS = "pcs", "шт"

    name = models.CharField("Наименование", max_length=255)
    material_type = models.CharField(
        "Тип сырья",
        max_length=20,
        choices=MaterialTypes.choices,
    )
    unit = models.CharField(
        "Ед. измерения",
        max_length=10,
        choices=Units.choices,
        default=Units.KG,
    )
    min_stock = models.DecimalField(
        "Минимальный остаток",
        max_digits=12,
        decimal_places=3,
        default=0,
    )
    current_stock = models.DecimalField(
        "Текущий остаток",
        max_digits=12,
        decimal_places=3,
        default=0,
    )

    class Meta:
        verbose_name = "Сырьё"
        verbose_name_plural = "Сырьё"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def status(self):

        if self.current_stock <= 0:
            return "empty"
        if self.current_stock < self.min_stock:
            return "low"
        return "ok"


class RawMaterialMovement(TimeStampedModel):
  
    class OperationTypes(models.TextChoices):
        IN = "in", "Поступление"
        OUT = "out", "Расход"

    material = models.ForeignKey(
        RawMaterial,
        on_delete=models.CASCADE,
        related_name="movements",
    )
    operation_type = models.CharField(
        "Тип операции",
        max_length=3,
        choices=OperationTypes.choices,
    )
    quantity = models.DecimalField(
        "Количество",
        max_digits=12,
        decimal_places=3,
    )
    document = models.CharField(
        "Документ (накладная, заказ и т.п.)",
        max_length=255,
        blank=True,
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="raw_material_operations",
    )

    class Meta:
        verbose_name = "Движение сырья"
        verbose_name_plural = "Движения сырья"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.material} {self.operation_type} {self.quantity}"


    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            from django.db.models import F
            sign = 1 if self.operation_type == self.OperationTypes.IN else -1
            RawMaterial.objects.filter(pk=self.material_id).update(
                current_stock=F("current_stock") + sign * self.quantity
            )


class FinishedProduct(TimeStampedModel):
    name = models.CharField("Наименование", max_length=255)
    sku = models.CharField("Артикул (SKU)", max_length=64, unique=True)
    stock = models.DecimalField(
        "Остаток на складе",
        max_digits=12,
        decimal_places=3,
        default=0,
    )
    reserved = models.DecimalField(
        "Резерв (под подтверждённые заказы)",
        max_digits=12,
        decimal_places=3,
        default=0,
    )

    class Meta:
        verbose_name = "Готовая продукция"
        verbose_name_plural = "Готовая продукция"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def available(self):
        return self.stock - self.reserved
