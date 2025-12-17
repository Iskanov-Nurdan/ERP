from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Recipe(TimeStampedModel):
    name = models.CharField("Название", max_length=255)
    product_name = models.CharField("Продукт", max_length=255, blank=True, default="")
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="created_recipes",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Рецептура"
        verbose_name_plural = "Рецептуры"

    def __str__(self):
        return self.name


class RecipeVersion(TimeStampedModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="versions")
    version = models.PositiveIntegerField("Версия", default=1)
    is_active = models.BooleanField(default=True)
    note = models.CharField("Комментарий", max_length=255, blank=True, default="")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="created_recipe_versions",
    )

    class Meta:
        ordering = ["-version", "-created_at"]
        unique_together = [("recipe", "version")]
        verbose_name = "Версия рецептуры"
        verbose_name_plural = "Версии рецептур"

    def __str__(self):
        return f"{self.recipe.name} v{self.version}"


class RecipeItem(models.Model):
    """
    Норма расхода: сколько кг сырья нужно на 1 кг готовой продукции
    (если у тебя нормы на штуку — потом расширим)
    """
    version = models.ForeignKey(RecipeVersion, on_delete=models.CASCADE, related_name="items")

    # берём сырьё из твоего склада
    material = models.ForeignKey(
        "sclad.RawMaterial",
        on_delete=models.PROTECT,
        related_name="recipe_items",
        verbose_name="Сырьё",
    )

    qty_per_kg = models.DecimalField("Норма (кг на 1 кг)", max_digits=12, decimal_places=6)

    class Meta:
        verbose_name = "Компонент рецептуры"
        verbose_name_plural = "Компоненты рецептуры"

    def __str__(self):
        return f"{self.material} = {self.qty_per_kg}/kg"
