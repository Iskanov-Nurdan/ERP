from django.db import models
from django.conf import settings

from apps.sclad.models import Recipe
from apps.production_control.models import ProductionLine


class ProductionOrder(models.Model):
    STATUS_CREATED = 'CREATED'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_DONE = 'DONE'

    STATUS_CHOICES = (
        (STATUS_CREATED, 'Создан'),
        (STATUS_IN_PROGRESS, 'В работе'),
        (STATUS_DONE, 'Завершён'),
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.PROTECT,
        related_name='production_orders'
    )

    production_line = models.ForeignKey(
        ProductionLine,
        on_delete=models.PROTECT,
        related_name='production_orders'
    )

    planned_quantity = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_production_orders'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.id} — {self.recipe}'
