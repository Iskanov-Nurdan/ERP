from django.contrib import admin
from .models import RawMaterial, RawMaterialReceipt, RawMaterialMovement, FinishedProductBatch, FinishedProductMovement


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



@admin.register(FinishedProductBatch)
class FinishedProductBatchAdmin(admin.ModelAdmin):
    list_display = ['batch_number', 'product_name', 'quantity', 'status', 'production_date', 'acceptance_date', 'accepted_by']
    list_filter = ['status', 'product_name', 'production_date']
    search_fields = ['batch_number', 'product_name']
    readonly_fields = ['acceptance_date', 'created_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('batch_number', 'product_name', 'quantity', 'status')
        }),
        ('Связи', {
            'fields': ('production_batch', 'accepted_by')
        }),
        ('Даты', {
            'fields': ('production_date', 'acceptance_date', 'created_at')
        }),
        ('Комментарий', {
            'fields': ('comment',),
            'classes': ('collapse',)
        }),
    )


@admin.register(FinishedProductMovement)
class FinishedProductMovementAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'operation_type', 'quantity', 'user', 'created_at']
    list_filter = ['operation_type', 'created_at']
    search_fields = ['product_name', 'batch__batch_number', 'finished_batch__batch_number']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Операция', {
            'fields': ('operation_type', 'quantity', 'product_name')
        }),
        ('Связи', {
            'fields': ('batch', 'finished_batch', 'user')
        }),
        ('Дополнительно', {
            'fields': ('comment', 'created_at')
        }),
    )