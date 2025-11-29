from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "admin", "Администратор"
        WAREHOUSE_MANAGER = "warehouse_manager", "Кладовщик сырья"
        PRODUCTION_WORKER = "production_worker", "Работник производства"
        PRODUCTION_OPERATOR = "production_operator", "Оператор производства"
        QUALITY_CONTROL = "quality_control", "Специалист по качеству"
        SALES_MANAGER = "sales_manager", "Менеджер по продажам"
        LOGISTICS_MANAGER = "logistics_manager", "Менеджер по логистике"

    role = models.CharField(
        max_length=50,
        choices=Roles.choices,
        default=Roles.PRODUCTION_WORKER
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
