from django.db import models
from django.conf import settings


class ProductionLine(models.Model):
    class Status(models.TextChoices):
        RUNNING = "running", "Работает"
        STOPPED = "stopped", "Остановлена"
        MAINTENANCE = "maintenance", "Обслуживание"

    identifier = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Идентификатор линии",
        help_text="Код/номер линии, например L1, EXT-01",
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Название",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RUNNING,
        verbose_name="Статус",
    )

    # скорость в процентах или условных единицах
    speed_percent = models.PositiveIntegerField(
        verbose_name="Скорость, %",
        default=0,
        help_text="0–100, можно использовать как относительную скорость",
    )

    # выпуск за смену — условно штук, кг и т.п.
    output_per_shift = models.PositiveIntegerField(
        verbose_name="Выпуск за смену",
        default=0,
        help_text="Количество произведённой продукции за смену",
    )

    last_maintenance_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Последнее обслуживание",
    )

    monitored_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="production_lines",
        verbose_name="Ответственный оператор",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    def __str__(self):
        return f"{self.identifier} — {self.name} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Производственная линия"
        verbose_name_plural = "Производственные линии"
        ordering = ["identifier"]
