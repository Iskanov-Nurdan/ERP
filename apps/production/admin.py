from django.contrib import admin
from .models import ProductionOrder


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client_name",
        "product_name",
        "color",
        "quantity_planned",
        "produced_quantity",
        "defect_quantity",
        "status",
        "current_stage",
        "priority",
        "production_line",
        "created_at",
    )
    list_filter = ("status", "current_stage", "priority", "production_line")
    search_fields = ("client_name", "product_name", "color")
    ordering = ("-created_at",)
