import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from django.utils import timezone


class ProductionBatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_number = models.CharField("Партия ГП", max_length=120, unique=True)

    order = models.ForeignKey(
        'order.ProductionOrder',
        on_delete=models.PROTECT,
        related_name='production_batches',
        verbose_name="Производственный заказ",
        null=True,
        blank=True
    )

    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Оператор",
        related_name='produced_batches'
    )

    product_name = models.CharField("Продукт", max_length=255)
    quantity_produced = models.DecimalField(
        "Количество произведено",
        max_digits=14,
        decimal_places=1,
        validators=[MinValueValidator(0.1)],
    )
    produced_at = models.DateTimeField("Дата производства")
    created_at = models.DateTimeField(auto_now_add=True)

    quality_status = models.CharField(
        "Статус ОТК",
        max_length=20,
        choices=[
            ('pending', 'Ожидает ОТК'),
            ('passed', 'Принято'),
            ('passed_with_defects', 'Принято с браком'),
            ('failed', 'Полный брак'),
        ],

        default='pending'
    )

    # Новые поля для контроля качества
    quality_checked_at = models.DateTimeField(
        "Дата проверки ОТК",
        null=True,
        blank=True
    )

    quality_inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Инспектор ОТК",
        related_name='quality_checked_batches'
    )

    quantity_accepted = models.DecimalField(
        "Принято (шт)",
        max_digits=14,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )

    quantity_defective = models.DecimalField(
        "Брак (шт)",
        max_digits=14,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )

    defect_reason = models.TextField(
        "Причина брака",
        blank=True,
        null=True
    )

    quality_comment = models.TextField(
        "Комментарий ОТК",
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["-produced_at"]
        verbose_name = "Партия производства"
        verbose_name_plural = "Партии производства"

    def __str__(self):
        return f"{self.product_name} ({self.batch_number})"


class ProductionComponent(models.Model):
    production = models.ForeignKey(
        ProductionBatch,
        on_delete=models.CASCADE,
        related_name="components",
        verbose_name="Партия производства"
    )
    material = models.ForeignKey(
        "sclad.RawMaterial",
        on_delete=models.PROTECT,
        verbose_name="Сырьё"
    )
    receipt = models.ForeignKey(
        "sclad.RawMaterialReceipt",
        on_delete=models.PROTECT,
        verbose_name="Партия склада"
    )
    quantity_used = models.DecimalField(
        "Списано",
        max_digits=14,
        decimal_places=1,
        validators=[MinValueValidator(0.1)],
    )
    unit = models.CharField("Единица измерения", max_length=20, default="kg")

    class Meta:
        verbose_name = "Компонент производства"
        verbose_name_plural = "Компоненты производства"

    def __str__(self):
        return f"{self.material.name} - {self.quantity_used} {self.unit}"



