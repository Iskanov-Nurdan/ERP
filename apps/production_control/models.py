from django.db import models


class ProductionLine(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название линии", unique=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Производственная линия"
        verbose_name_plural = "Производственные линии"
        ordering = ["name"]

    def __str__(self):
        return self.name
