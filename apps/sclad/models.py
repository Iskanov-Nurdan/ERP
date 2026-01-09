
from django.conf import settings
import uuid
from django.db import models
from django.core.validators import MinValueValidator
from apps.production.models import ProductionBatch


class RawMaterial(models.Model):
    class Unit(models.TextChoices):
        G = "g", "г"
        KG = "kg", "кг"
        ML = "ml", "мл"
        L = "l", "л"

    name = models.CharField("Название", max_length=255, unique=True)
    unit = models.CharField(
        "Единица измерения",
        max_length=5,
        choices=Unit.choices,
        default=Unit.KG,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Сырьё"
        verbose_name_plural = "Справочник сырья"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} ({self.get_unit_display()})"


class RawMaterialReceipt(models.Model):
    material = models.ForeignKey(
        RawMaterial,
        on_delete=models.PROTECT,
        related_name="receipts",
        verbose_name="Сырьё",
    )
    date = models.DateField("Дата прихода")
    quantity = models.DecimalField(
        "Количество",
        max_digits=14,
        decimal_places=1,
        validators=[MinValueValidator(0.1)],
    )

    batch_number = models.CharField("Номер партии", max_length=120, blank=True, default="")
    supplier = models.CharField("Поставщик", max_length=255, blank=True, default="")
    comment = models.CharField("Комментарий", max_length=500, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Приход сырья"
        verbose_name_plural = "Приход сырья"
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.material.name} +{self.quantity} {self.material.unit} ({self.batch_number})"


class RawMaterialMovement(models.Model):
    class Operation(models.TextChoices):
        IN_ = "in", "Приход"
        OUT = "out", "Расход"

    material = models.ForeignKey(
        RawMaterial,
        on_delete=models.PROTECT,
        related_name="movements",
        verbose_name="Сырьё",
    )
    operation_type = models.CharField("Тип операции", max_length=10, choices=Operation.choices)
    quantity = models.DecimalField("Количество", max_digits=14, decimal_places=1)

    receipt = models.ForeignKey(
        RawMaterialReceipt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements",
        verbose_name="Документ прихода",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Движение сырья"
        verbose_name_plural = "Движения сырья"
        ordering = ["-created_at", "-id"]

    def __str__(self):
        sign = "+" if self.operation_type == self.Operation.IN_ else "-"
        return f"{self.material.name} {sign}{self.quantity}"


class Recipe(models.Model):
    name = models.CharField("Название рецепта", max_length=255)
    product_name = models.CharField("Товар", max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}"


class RecipeItem(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Рецепт",
    )
    material = models.ForeignKey(
        RawMaterial,
        on_delete=models.PROTECT,
        related_name="recipe_items",
        verbose_name="Сырьё",
    )
    quantity = models.DecimalField(
        "Количество",
        max_digits=14,
        decimal_places=1,
        validators=[MinValueValidator(0.1)],
    )

    class Meta:
        verbose_name = "Сырьё в рецепте"
        verbose_name_plural = "Сырьё в рецептах"
        unique_together = ("recipe", "material")

    def __str__(self):
        return f"{self.material.name} — {self.quantity}"


# models.py - добавь в конец
class FinishedProductBatch(models.Model):
    """Партия готовой продукции на складе"""

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Доступно'
        RESERVED = 'reserved', 'Зарезервировано'
        SHIPPED = 'shipped', 'Отгружено'
        EXPIRED = 'expired', 'Просрочено'

    batch_number = models.CharField("Номер партии ГП", max_length=120, unique=True)
    product_name = models.CharField("Продукт", max_length=255)
    quantity = models.DecimalField(
        "Количество",
        max_digits=14,
        decimal_places=1,
        validators=[MinValueValidator(0.1)],
    )
    production_batch = models.ForeignKey(
        ProductionBatch,
        on_delete=models.PROTECT,
        related_name='finished_batches',
        verbose_name="Партия производства",
        null=True,
        blank=True
    )
    production_date = models.DateField("Дата производства")
    acceptance_date = models.DateTimeField("Дата приёмки", auto_now_add=True)
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Принял на склад",
        related_name='accepted_finished_batches'
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE
    )
    comment = models.TextField("Комментарий", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Партия готовой продукции"
        verbose_name_plural = "Партии готовой продукции"
        ordering = ["-acceptance_date"]

    def __str__(self):
        return f"{self.batch_number} - {self.product_name} ({self.quantity})"


class FinishedProductMovement(models.Model):
    """Движение готовой продукции"""

    class Operation(models.TextChoices):
        PRODUCTION = 'production', 'Производство'
        QUALITY_ACCEPTED = 'quality_accepted', 'Принято ОТК'
        QUALITY_REJECTED = 'quality_rejected', 'Брак ОТК'
        WAREHOUSE_ACCEPTANCE = 'warehouse_acceptance', 'Приёмка на склад ГП'
        SHIPMENT = 'shipment', 'Отгрузка'
        RETURN = 'return', 'Возврат'
        WRITE_OFF = 'write_off', 'Списание'

    batch = models.ForeignKey(
        ProductionBatch,
        on_delete=models.CASCADE,
        related_name='product_movements',
        verbose_name="Партия производства",
        null=True,
        blank=True
    )
    finished_batch = models.ForeignKey(
        FinishedProductBatch,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name="Партия ГП",
        null=True,
        blank=True
    )
    operation_type = models.CharField(
        "Тип операции",
        max_length=30,
        choices=Operation.choices
    )
    quantity = models.DecimalField(
        "Количество",
        max_digits=14,
        decimal_places=1,
        validators=[MinValueValidator(0.1)],
    )
    product_name = models.CharField("Продукт", max_length=255)
    created_at = models.DateTimeField("Дата операции", auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пользователь"
    )
    comment = models.TextField("Комментарий", blank=True, null=True)

    class Meta:
        verbose_name = "Движение готовой продукции"
        verbose_name_plural = "Движения готовой продукции"

