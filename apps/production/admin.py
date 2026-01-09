# admin.py
from django.contrib import admin
from .models import ProductionBatch, ProductionComponent


class ProductionComponentInline(admin.TabularInline):
    model = ProductionComponent
    extra = 0
    readonly_fields = (
        "material",
        "receipt",
        "quantity_used",
    )


@admin.register(ProductionBatch)
class ProductionBatchAdmin(admin.ModelAdmin):
    list_display = (
        "batch_number",
        "product_name",
        "quantity_produced",
        "produced_at",
        "created_at",
    )
    search_fields = ("batch_number", "product_name")
    list_filter = ("produced_at",)
    inlines = [ProductionComponentInline]
    readonly_fields = ("created_at",)


@admin.register(ProductionComponent)
class ProductionComponentAdmin(admin.ModelAdmin):
    list_display = (
        "production",
        "material",
        "receipt",
        "quantity_used",
    )
    search_fields = (
        "production__batch_number",
        "material__name",
        "receipt__batch_number",
    )
