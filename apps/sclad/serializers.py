from rest_framework import serializers
from .models import RawMaterial, RawMaterialMovement, FinishedProduct


class RawMaterialSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField()

    class Meta:
        model = RawMaterial
        fields = [
            "id",
            "name",
            "material_type",
            "unit",
            "min_stock",
            "current_stock",
            "status",
            "created_at",
            "updated_at",
        ]


class RawMaterialMovementSerializer(serializers.ModelSerializer):
    material_name = serializers.ReadOnlyField(source="material.name")
    performed_by_email = serializers.ReadOnlyField(source="performed_by.email")

    class Meta:
        model = RawMaterialMovement
        fields = [
            "id",
            "material",
            "material_name",
            "operation_type",
            "quantity",
            "document",
            "performed_by",
            "performed_by_email",
            "created_at",
        ]
        read_only_fields = ["performed_by", "performed_by_email", "created_at"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Количество должно быть больше нуля.")
        return value


class FinishedProductSerializer(serializers.ModelSerializer):
    available = serializers.ReadOnlyField()

    class Meta:
        model = FinishedProduct
        fields = [
            "id",
            "name",
            "sku",
            "stock",
            "reserved",
            "available",
            "created_at",
            "updated_at",
        ]
