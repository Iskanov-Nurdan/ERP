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
    email = models.EmailField(unique=True)

    class SystemRoles(models.TextChoices):
        OWNER = "owner", "Владелец"
        ADMIN = "admin", "Администратор"
        USER = "user", "Пользователь"


    system_role = models.CharField(
        max_length=20,
        choices=SystemRoles.choices,
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="users"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "system_role"]  

    def __str__(self):
        return f"{self.email} ({self.system_role})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
