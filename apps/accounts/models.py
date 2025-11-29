from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"


class User(AbstractUser):
    class SystemRoles(models.TextChoices):
        OWNER = "owner", "Владелец"
        ADMIN = "admin", "Администратор"

    system_role = models.CharField(
        max_length=20,
        choices=SystemRoles.choices,
        default=SystemRoles.ADMIN
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="users"
    )

    def __str__(self):
        return f"{self.username} ({self.system_role})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"