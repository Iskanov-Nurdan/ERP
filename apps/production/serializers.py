from rest_framework import serializers
from .models import ProductionOrder


class ProductionOrderSerializer(serializers.ModelSerializer):
    current_stage_label = serializers.CharField(source="get_current_stage_display", read_only=True)
    priority_label = serializers.CharField(source="get_priority_display", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    created_by_email = serializers.ReadOnlyField(source="created_by.email")

    class Meta:
        model = ProductionOrder
        fields = [
            "id",
            "client_name",
            "product_name",
            "color",
            "quantity_planned",
            "produced_quantity",
            "defect_quantity",
            "production_line",

            "current_stage",
            "current_stage_label",
            "priority",
            "priority_label",
            "status",
            "status_label",

            "started_at",
            "completed_at",
            "comment",

            "created_by",
            "created_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_by",
            "created_by_email",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]

    def validate_quantity_planned(self, value):
        if value <= 0:
            raise serializers.ValidationError("План (кг) должен быть больше нуля.")
        return value

    def validate(self, attrs):
        # если заказ уже завершён/в браке — нельзя менять ключевые поля
        instance = getattr(self, "instance", None)
        if instance and instance.status in [ProductionOrder.Status.DONE, ProductionOrder.Status.REJECTED]:
            forbidden = {"quantity_planned", "production_line", "product_name", "client_name"}
            touched = forbidden.intersection(set(attrs.keys()))
            if touched:
                raise serializers.ValidationError("Нельзя изменять завершённый/отбракованный заказ.")
        return attrs


class ProductionOrderCompleteSerializer(serializers.Serializer):
    produced_quantity = serializers.DecimalField(max_digits=12, decimal_places=3)
    defect_quantity = serializers.DecimalField(max_digits=12, decimal_places=3, required=False, default=0)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_produced_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Произведено (кг) должно быть > 0.")
        return value

    def validate_defect_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Брак (кг) не может быть отрицательным.")
        return value


class ProductionOrderRejectSerializer(serializers.Serializer):
    defect_weight = serializers.DecimalField(max_digits=12, decimal_places=3)
    reason = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_defect_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError("Вес брака (кг) должен быть > 0.")
        return value
