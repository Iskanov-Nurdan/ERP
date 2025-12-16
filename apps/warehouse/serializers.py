from rest_framework import serializers
from .models import Warehouse, Material, MaterialStock, MaterialMovement, MaterialReservation


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ["id", "name", "address", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class MaterialSerializer(serializers.ModelSerializer):
    unit_label = serializers.CharField(source="get_unit_display", read_only=True)

    class Meta:
        model = Material
        fields = [
            "id", "name", "code", "unit", "unit_label",
            "price_per_kg", "supplier", "min_stock",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_min_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("min_stock не может быть отрицательным.")
        return value


class MaterialStockSerializer(serializers.ModelSerializer):
    material_name = serializers.ReadOnlyField(source="material.name")
    warehouse_name = serializers.ReadOnlyField(source="warehouse.name")

    class Meta:
        model = MaterialStock
        fields = [
            "id",
            "material", "material_name",
            "warehouse", "warehouse_name",
            "quantity",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MaterialMovementSerializer(serializers.ModelSerializer):
    movement_type_label = serializers.CharField(source="get_movement_type_display", read_only=True)
    material_name = serializers.ReadOnlyField(source="material.name")
    created_by_email = serializers.ReadOnlyField(source="created_by.email")

    class Meta:
        model = MaterialMovement
        fields = [
            "id",
            "movement_type", "movement_type_label",
            "material", "material_name",
            "from_warehouse", "to_warehouse",
            "quantity", "notes",
            "created_by", "created_by_email",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_by_email", "created_at", "updated_at"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("quantity должна быть > 0.")
        return value


class MaterialReservationSerializer(serializers.ModelSerializer):
    material_name = serializers.ReadOnlyField(source="material.name")
    warehouse_name = serializers.ReadOnlyField(source="warehouse.name")
    created_by_email = serializers.ReadOnlyField(source="created_by.email")

    class Meta:
        model = MaterialReservation
        fields = [
            "id",
            "material", "material_name",
            "warehouse", "warehouse_name",
            "production_order_id",
            "quantity",
            "created_by", "created_by_email",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_by_email", "created_at", "updated_at"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("quantity должна быть > 0.")
        return value
