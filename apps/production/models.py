from django.db import models
from django.conf import settings
from django.utils import timezone

from apps.production_control.models import ProductionLine


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class ProductionOrder(TimeStampedModel):
    class Stages(models.TextChoices):
        MIXING = "mixing", "Смешивание"
        EXTRUSION = "extrusion", "Экструзия"
        FORMING = "forming", "Формовка"
        COOLING = "cooling", "Охлаждение"
        PACKING = "packing", "Упаковка"

    STAGE_FLOW = [
        Stages.MIXING,
        Stages.EXTRUSION,
        Stages.FORMING,
        Stages.COOLING,
        Stages.PACKING,
    ]

    class Priority(models.TextChoices):
        LOW = "low", "Низкий"
        MEDIUM = "medium", "Средний"
        HIGH = "high", "Высокий"

    class Status(models.TextChoices):
        NEW = "new", "Новый"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Завершён"
        REJECTED = "rejected", "В браке"
        CANCELED = "canceled", "Отменён"

    client_name = models.CharField("Клиент", max_length=255)
    product_name = models.CharField("Продукт", max_length=255)
    color = models.CharField("Цвет", max_length=64, blank=True, default="")

    # план/факт в кг (как у тебя в ТЗ)
    quantity_planned = models.DecimalField("План (кг)", max_digits=12, decimal_places=3)
    produced_quantity = models.DecimalField("Произведено (кг)", max_digits=12, decimal_places=3, default=0)
    defect_quantity = models.DecimalField("Брак (кг)", max_digits=12, decimal_places=3, default=0)

    production_line = models.ForeignKey(
        ProductionLine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Производственная линия",
    )

    current_stage = models.CharField(
        "Текущий этап",
        max_length=32,
        choices=Stages.choices,
        default=Stages.MIXING,
    )

    priority = models.CharField(
        "Приоритет",
        max_length=16,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    status = models.CharField(
        "Статус",
        max_length=16,
        choices=Status.choices,
        default=Status.NEW,
    )

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_production_orders",
        verbose_name="Создано пользователем",
    )

    comment = models.TextField("Комментарий", blank=True)

    class Meta:
        verbose_name = "Заказ на производство"
        verbose_name_plural = "Заказы на производство"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.client_name} — {self.product_name} ({self.quantity_planned} кг)"

    def move_to_next_stage(self):
        stages = [s.value for s in self.STAGE_FLOW]
        try:
            idx = stages.index(self.current_stage)
        except ValueError:
            self.current_stage = self.Stages.MIXING
            self.status = self.Status.IN_PROGRESS
            return

        if idx < len(stages) - 1:
            self.current_stage = stages[idx + 1]
            self.status = self.Status.IN_PROGRESS
        else:
            self.current_stage = stages[-1]
            self.status = self.Status.DONE
            self.completed_at = timezone.now()
