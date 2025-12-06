from django.apps import AppConfig


class ProductionControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.production_control'
