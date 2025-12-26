from django.db import transaction
from decimal import Decimal
from django.db.models import Sum, Case, When, Value, DecimalField
from django.db.models.functions import Coalesce
from rest_framework import serializers

from .models import (
    RawMaterial,
    RawMaterialReceipt,
    RawMaterialMovement,
    Recipe,
    RecipeItem,
)


# =======================
# СЫРЬЁ
# =======================
class RawMaterialSerializer(serializers.ModelSerializer):
    unit_label = serializers.CharField(source="get_unit_display", read_only=True)

    class Meta:
        model = RawMaterial
        fields = ["id", "name", "unit", "unit_label", "created_at", "updated_at"]
        read_only_fields = ["id", "unit_label", "created_at", "updated_at"]


# =======================
# ПРИХОД
# =======================
class RawMaterialReceiptSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source="material.name", read_only=True)
    unit = serializers.CharField(source="material.unit", read_only=True)
    unit_label = serializers.CharField(source="material.get_unit_display", read_only=True)

    class Meta:
        model = RawMaterialReceipt
        fields = [
            "id",
            "date",
            "material",
            "material_name",
            "quantity",
            "unit",
            "unit_label",
            "batch_number",
            "supplier",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "material_name", "unit", "unit_label", "created_at"]


# =======================
# БАЛАНС
# =======================
class RawMaterialBatchSerializer(serializers.Serializer):
    batch_number = serializers.CharField()
    qty = serializers.DecimalField(max_digits=14, decimal_places=3)
    date = serializers.DateField()
    supplier = serializers.CharField(allow_blank=True, required=False)


class RawMaterialBatchesBalanceSerializer(serializers.Serializer):
    material_id = serializers.IntegerField()
    material_name = serializers.CharField()
    unit_label = serializers.CharField()
    total = serializers.DecimalField(max_digits=14, decimal_places=3)
    batches = RawMaterialBatchSerializer(many=True)

# =======================
# РЕЦЕПТЫ
# =======================
class RecipeItemSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source="material.name", read_only=True)
    unit_label = serializers.CharField(source="material.get_unit_display", read_only=True)

    class Meta:
        model = RecipeItem
        fields = ["id", "material", "material_name", "quantity", "unit_label"]


class RecipeItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeItem
        fields = ["material", "quantity"]


class RecipeSerializer(serializers.ModelSerializer):
    items = RecipeItemSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ["id", "name", "product_name", "items"]


class RecipeWriteSerializer(serializers.ModelSerializer):
    items = RecipeItemWriteSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ["id", "name", "product_name", "items"]
        read_only_fields = ["id"]

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Добавь хотя бы одно сырьё в состав рецепта.")

        seen = set()
        for it in items:
            mat = it.get("material")
            mat_id = mat.id if hasattr(mat, "id") else int(mat)
            if mat_id in seen:
                raise serializers.ValidationError("Одно и то же сырьё нельзя добавлять дважды.")
            seen.add(mat_id)
        return items

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop("items", [])
        recipe = Recipe.objects.create(**validated_data)
        RecipeItem.objects.bulk_create(
            [RecipeItem(recipe=recipe, **it) for it in items]
        )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        items = validated_data.pop("items", None)

        # обновляем поля рецепта
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # если пришёл состав — полностью пересобираем
        if items is not None:
            instance.items.all().delete()
            RecipeItem.objects.bulk_create(
                [RecipeItem(recipe=instance, **it) for it in items]
            )

        return instance