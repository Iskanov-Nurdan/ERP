from django.conf import settings
from django.db import models
from django.utils import timezone
from apps.production_control.models import ProductionLine


class Shift(models.Model):
    line = models.ForeignKey(
        ProductionLine,
        on_delete=models.PROTECT,
        related_name="shifts",
    )

    STATUS_ACTIVE = "active"
    STATUS_CLOSED = "closed"

    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Активна"),
        (STATUS_CLOSED, "Закрыта"),
    )

    date = models.DateField()
    line = models.ForeignKey(
        ProductionLine,
        on_delete=models.PROTECT,
        related_name="shifts",
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="managed_shifts",
    )

    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def close(self):
        self.ended_at = timezone.now()
        self.status = self.STATUS_CLOSED
        self.save()

    def __str__(self):
        return f"{self.date} — {self.line}"
