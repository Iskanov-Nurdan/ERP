from django.db import models
from django.conf import settings


class Shipment(models.Model):
    class Status(models.TextChoices):
        PLANNING = "planning", "Планирование"
        LOADING = "loading", "Погрузка"
        IN_TRANSIT = "in_transit", "В пути"
        DELIVERED = "delivered", "Доставлено"

    client_name = models.CharField(
        max_length=255,
        verbose_name="Клиент",
    )
    city = models.CharField(
        max_length=255,
        verbose_name="Город / пункт доставки",
    )
    pallets_count = models.PositiveIntegerField(
        verbose_name="Кол-во паллет",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNING,
        verbose_name="Статус",
    )

    eta_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Прогноз ETA (часы до доставки)",
        help_text="Можно оставлять пустым, если ещё не посчитан",
    )

    # кто создал/изменяет — на будущее
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_shipments",
        verbose_name="Создано пользователем",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    def __str__(self):
        return f"{self.client_name} → {self.city} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Отгрузка"
        verbose_name_plural = "Отгрузки"
        ordering = ["-created_at"]
