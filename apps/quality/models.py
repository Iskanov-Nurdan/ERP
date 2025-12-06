from django.db import models
from django.conf import settings


class QualityIssue(models.Model):
    class Severity(models.TextChoices):
        LOW = "low", "Низкая"
        MEDIUM = "medium", "Средняя"
        HIGH = "high", "Высокая"

    product_name = models.CharField(
        max_length=255,
        verbose_name="Продукт",
    )
    defect_type = models.CharField(
        max_length=255,
        verbose_name="Тип дефекта",
    )
    lot = models.CharField(
        max_length=100,
        verbose_name="Партия (lot)",
    )

    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
        default=Severity.MEDIUM,
        verbose_name="Важность",
    )

    corrective_actions = models.TextField(
        verbose_name="Корректирующие действия",
        blank=True,
    )

    detected_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата/время выявления",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quality_issues",
        verbose_name="Ответственный",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    def __str__(self):
        return f"{self.product_name} ({self.lot}) - {self.defect_type}"

    class Meta:
        verbose_name = "Несоответствие"
        verbose_name_plural = "Журнал несоответствий"
        ordering = ["-created_at"]
