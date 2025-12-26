from django.contrib import admin
from .models import RawMaterial, RawMaterialReceipt, RawMaterialMovement


@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "unit", "created_at")
    search_fields = ("name",)
    list_filter = ("unit",)


@admin.register(RawMaterialReceipt)
class RawMaterialReceiptAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "material", "quantity", "batch_number", "supplier")
    search_fields = ("material__name", "batch_number", "supplier")
    list_filter = ("date",)


@admin.register(RawMaterialMovement)
class RawMaterialMovementAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "material", "operation_type", "quantity", "receipt")
    list_filter = ("operation_type", "created_at")
    search_fields = ("material__name",)
