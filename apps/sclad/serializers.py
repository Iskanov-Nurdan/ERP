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
    FinishedProductMovement,
    FinishedProductBatch
)


class RawMaterialSerializer(serializers.ModelSerializer):
    unit_label = serializers.CharField(source="get_unit_display", read_only=True)

    class Meta:
        model = RawMaterial
        fields = ["id", "name", "unit", "unit_label", "created_at", "updated_at"]
        read_only_fields = ["id", "unit_label", "created_at", "updated_at"]


class RawMaterialReceiptSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source="material.name", read_only=True)
    unit = serializers.CharField(source="material.unit", read_only=True)
    unit_label = serializers.CharField(source="material.get_unit_display", read_only=True)
    quantity_display = serializers.SerializerMethodField()

    class Meta:
        model = RawMaterialReceipt
        fields = [
            "id",
            "date",
            "material",
            "material_name",
            "quantity",
            "quantity_display",
            "unit",
            "unit_label",
            "batch_number",
            "supplier",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "material_name", "unit", "unit_label", "created_at"]

    def get_quantity_display(self, obj):
        qty = float(obj.quantity)
        if qty.is_integer():
            return int(qty)
        return qty


class RawMaterialBatchSerializer(serializers.Serializer):
    batch_number = serializers.CharField()
    qty = serializers.DecimalField(max_digits=14, decimal_places=1)
    date = serializers.DateField()
    supplier = serializers.CharField(allow_blank=True, required=False)
    receipt_id = serializers.IntegerField()  # ✅ ДОБАВЛЕНО
    unit_label = serializers.CharField(required=False)  # ✅ для удобства


class RawMaterialBatchesBalanceSerializer(serializers.Serializer):
    material_id = serializers.IntegerField()
    material_name = serializers.CharField()
    unit_label = serializers.CharField()
    total = serializers.DecimalField(max_digits=14, decimal_places=1)
    batches = RawMaterialBatchSerializer(many=True)


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

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items is not None:
            instance.items.all().delete()
            RecipeItem.objects.bulk_create(
                [RecipeItem(recipe=instance, **it) for it in items]
            )

        return instance




# serializers.py - добавь в конец
class FinishedProductBatchSerializer(serializers.ModelSerializer):
    accepted_by_name = serializers.CharField(source='accepted_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = FinishedProductBatch
        fields = [
            'id', 'batch_number', 'product_name', 'quantity',
            'production_date', 'acceptance_date', 'accepted_by_name',
            'status', 'status_display', 'comment', 'production_batch_id'
        ]


class FinishedProductBatchCreateSerializer(serializers.ModelSerializer):
    production_batch_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = FinishedProductBatch
        fields = [
            'batch_number', 'product_name', 'quantity',
            'production_batch_id', 'production_date', 'comment'
        ]

    def validate_batch_number(self, value):
        if FinishedProductBatch.objects.filter(batch_number=value).exists():
            raise serializers.ValidationError("Партия ГП с таким номером уже существует")
        return value

    @transaction.atomic
    def create(self, validated_data):
        production_batch_id = validated_data.pop('production_batch_id')
        request = self.context.get('request')

        try:
            production_batch = ProductionBatch.objects.get(id=production_batch_id)
        except ProductionBatch.DoesNotExist:
            raise serializers.ValidationError({
                "production_batch_id": "Партия производства не найдена"
            })

        # Проверяем, что партия принята ОТК
        if production_batch.quality_status not in ['passed', 'passed_with_defects']:
            raise serializers.ValidationError({
                "production_batch_id": "Партия не принята ОТК"
            })

        # Проверяем, что ещё не принята на склад
        if hasattr(production_batch, 'finished_batches') and production_batch.finished_batches.exists():
            raise serializers.ValidationError({
                "production_batch_id": "Партия уже принята на склад ГП"
            })

        validated_data['production_batch'] = production_batch
        validated_data['accepted_by'] = request.user

        # Создаем партию ГП
        finished_batch = FinishedProductBatch.objects.create(**validated_data)

        # Создаем движение
        FinishedProductMovement.objects.create(
            batch=production_batch,
            finished_batch=finished_batch,
            operation_type=FinishedProductMovement.Operation.WAREHOUSE_ACCEPTANCE,
            quantity=finished_batch.quantity,
            product_name=finished_batch.product_name,
            user=request.user,
            comment=f"Приёмка на склад ГП. {validated_data.get('comment', '')}"
        )

        return finished_batch