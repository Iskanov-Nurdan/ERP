from django.contrib import admin
from .models import ProductionOrder


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client_name",
        "product_name",
        "quantity",
        "current_stage",
        "priority",
        "status",
        "created_by",
        "created_at",
    )
    list_filter = ("current_stage", "priority", "status")
    search_fields = ("client_name", "product_name")
