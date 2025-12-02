from rest_framework import serializers
from .models import ProductionOrder


class ProductionOrderSerializer(serializers.ModelSerializer):
    current_stage_label = serializers.CharField(
        source="get_current_stage_display", read_only=True
    )
    priority_label = serializers.CharField(
        source="get_priority_display", read_only=True
    )
    status_label = serializers.CharField(
        source="get_status_display", read_only=True
    )
    created_by_email = serializers.ReadOnlyField(source="created_by.email")

    class Meta:
        model = ProductionOrder
        fields = [
            "id",
            "client_name",
            "product_name",
            "quantity",
            "current_stage",
            "current_stage_label",
            "priority",
            "priority_label",
            "status",
            "status_label",
            "comment",
            "created_by",
            "created_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_by",
            "created_by_email",
            "created_at",
            "updated_at",
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Количество должно быть больше нуля.")
        return value
