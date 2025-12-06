from django.db import models


class ProductionLine(models.Model):
    class Status(models.TextChoices):
        RUNNING = "running", "Работает"
        STOPPED = "stopped", "Остановлена"

    code = models.CharField("Код линии", max_length=50, unique=True)
    name = models.CharField("Название", max_length=255)
    status = models.CharField(
        "Статус",
        max_length=10,
        choices=Status.choices,
        default=Status.STOPPED,
    )
    speed_percent = models.PositiveIntegerField(
        "Скорость, %",
        default=0,
        help_text="От 0 до 100",
    )
    output_per_shift = models.PositiveIntegerField(
        "Выпуск за смену, ед.",
        default=0,
    )
    last_update = models.DateTimeField("Последнее обновление", auto_now=True)

    def __str__(self):
        return f"{self.code} — {self.name}"

    class Meta:
        verbose_name = "Линия производства"
        verbose_name_plural = "Линии производства"