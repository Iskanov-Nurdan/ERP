from django.contrib import admin
from .models import CustomerOrder


@admin.register(CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order_number",
        "client_name",
        "amount",
        "status",
        "created_by",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("order_number", "client_name")
