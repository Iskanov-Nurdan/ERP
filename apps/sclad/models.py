from django.db import models
from django.core.validators import MinValueValidator


# =======================
# СЫРЬЁ
# =======================
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


# =======================
# ПРИХОД СЫРЬЯ
# =======================
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
        decimal_places=3,
        validators=[MinValueValidator(0.001)],
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
        return f"{self.material.name} +{self.quantity} {self.material.unit}"


# =======================
# ДВИЖЕНИЕ СЫРЬЯ
# =======================
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
    quantity = models.DecimalField("Количество", max_digits=14, decimal_places=3)

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


# =======================
# РЕЦЕПТ
# =======================
class Recipe(models.Model):
    # code = models.CharField("Код рецепта", max_length=50, unique=True)
    name = models.CharField("Название рецепта", max_length=255)
    product_name = models.CharField("Товар", max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}"


# =======================
# СЫРЬЁ В РЕЦЕПТЕ
# =======================
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
        decimal_places=3,
        validators=[MinValueValidator(0.001)],
    )

    class Meta:
        verbose_name = "Сырьё в рецепте"
        verbose_name_plural = "Сырьё в рецептах"
        unique_together = ("recipe", "material")

    def __str__(self):
        return f"{self.material.name} — {self.quantity}"
