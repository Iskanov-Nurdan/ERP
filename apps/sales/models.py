from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomerOrder(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_WORK = "in_work", "В работе"
        CONFIRMED = "confirmed", "Подтверждена"
        DECLINED = "declined", "Отказ"

    client_name = models.CharField("Клиент", max_length=255)
    order_number = models.CharField("Номер заказа", max_length=64, unique=True)
    amount = models.DecimalField("Сумма заказа", max_digits=14, decimal_places=2)

    status = models.CharField(
        "Статус",
        max_length=16,
        choices=Status.choices,
        default=Status.NEW,
    )

    comment = models.TextField("Комментарий", blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_customer_orders",
        verbose_name="Создано пользователем",
    )

    class Meta:
        verbose_name = "Заказ клиента"
        verbose_name_plural = "Заказы клиентов"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_number} — {self.client_name} ({self.amount})"
