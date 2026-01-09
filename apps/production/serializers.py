from rest_framework import serializers
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db import transaction
from django.apps import apps
from django.utils import timezone

from .models import ProductionBatch, ProductionComponent
from apps.sclad.models import RawMaterialReceipt, RawMaterialMovement

# Получаем модель ProductionOrder
ProductionOrder = apps.get_model('order', 'ProductionOrder')


class ProductionComponentWriteSerializer(serializers.Serializer):
    receipt_id = serializers.IntegerField()
    quantity_used = serializers.DecimalField(max_digits=14, decimal_places=1, min_value=Decimal('0.1'))

    def validate(self, data):
        receipt_id = data.get("receipt_id")
        quantity_used = data.get("quantity_used")

        try:
            receipt = RawMaterialReceipt.objects.get(id=receipt_id)
        except RawMaterialReceipt.DoesNotExist:
            raise serializers.ValidationError({
                "receipt_id": f"Приход с ID {receipt_id} не найден"
            })

        material = receipt.material

        in_qty = RawMaterialMovement.objects.filter(
            material_id=material.id,
            receipt_id=receipt_id,
            operation_type=RawMaterialMovement.Operation.IN_
        ).aggregate(total=Coalesce(Sum('quantity'), Decimal('0')))['total']

        out_qty = RawMaterialMovement.objects.filter(
            material_id=material.id,
            receipt_id=receipt_id,
            operation_type=RawMaterialMovement.Operation.OUT
        ).aggregate(total=Coalesce(Sum('quantity'), Decimal('0')))['total']

        available = in_qty - out_qty

        if quantity_used > available:
            batch_info = receipt.batch_number or f"#{receipt.id}"
            raise serializers.ValidationError({
                "quantity_used": f"Недостаточно сырья в партии '{batch_info}'. Доступно: {available}, требуется: {quantity_used}"
            })

        data['receipt'] = receipt
        data['material'] = material
        data['unit'] = material.unit
        return data


class ProductionBatchCreateSerializer(serializers.ModelSerializer):
    components = ProductionComponentWriteSerializer(many=True)

    production_order_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductionOrder.objects.all(),
        source='order',
        write_only=True,
        required=True
    )

    class Meta:
        model = ProductionBatch
        fields = [
            "id",
            "batch_number",
            "product_name",
            "quantity_produced",
            "produced_at",
            "components",
            "production_order_id",
        ]
        read_only_fields = ["id"]

    def validate_batch_number(self, value):
        if ProductionBatch.objects.filter(batch_number=value).exists():
            raise serializers.ValidationError("Партия с таким номером уже существует")
        return value

    def validate_components(self, value):
        if not value:
            raise serializers.ValidationError("Должен быть хотя бы один компонент")

        receipt_ids = [item.get('receipt_id') for item in value]
        if len(receipt_ids) != len(set(receipt_ids)):
            raise serializers.ValidationError("Нельзя использовать одну партию сырья дважды")

        return value

    @transaction.atomic
    def create(self, validated_data):
        components_data = validated_data.pop("components")
        order = validated_data.pop("order")

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['operator'] = request.user

        batch = ProductionBatch.objects.create(**validated_data)

        if order.status == ProductionOrder.STATUS_CREATED:
            order.status = ProductionOrder.STATUS_IN_PROGRESS
            order.save(update_fields=['status'])

        for component_data in components_data:
            receipt = component_data['receipt']
            material = component_data['material']
            quantity_used = component_data['quantity_used']
            unit = component_data['unit']

            RawMaterialMovement.objects.create(
                material=material,
                operation_type=RawMaterialMovement.Operation.OUT,
                quantity=quantity_used,
                receipt=receipt,
            )

            ProductionComponent.objects.create(
                production=batch,
                material=material,
                receipt=receipt,
                quantity_used=quantity_used,
                unit=unit
            )

        return batch


class ProductionComponentSerializer(serializers.ModelSerializer):
    receipt_id = serializers.IntegerField()
    raw_material_id = serializers.IntegerField(source='material.id')
    raw_material_name = serializers.CharField(source='material.name')
    batch_number = serializers.CharField(source='receipt.batch_number')
    supplier = serializers.CharField(source='receipt.supplier')
    unit_label = serializers.CharField(source='unit')

    class Meta:
        model = ProductionComponent
        fields = [
            'receipt_id',
            'raw_material_id',
            'raw_material_name',
            'batch_number',
            'quantity_used',
            'unit_label',
            'supplier',
        ]


class ProductionBatchListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка партий (GET /production/batches/list/)"""
    operator_name = serializers.CharField(
        source='operator.username',
        read_only=True,
        allow_null=True
    )

    order_id = serializers.IntegerField(
        source='order.id',
        read_only=True,
        allow_null=True
    )

    quality_status_display = serializers.CharField(
        source='get_quality_status_display',
        read_only=True
    )

    class Meta:
        model = ProductionBatch
        fields = [
            "id",
            "batch_number",
            "quality_status",
            "quality_status_display",
            "product_name",
            "quantity_produced",
            "produced_at",
            "operator_name",
            "order_id",
        ]


class ProductionBatchDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для деталей партии (GET /production/batches/{id}/)"""
    components = ProductionComponentSerializer(many=True, source='components.all', read_only=True)

    operator_name = serializers.CharField(
        source='operator.username',
        read_only=True,
        allow_null=True
    )

    order_id = serializers.IntegerField(
        source='order.id',
        read_only=True,
        allow_null=True
    )

    quality_status_display = serializers.CharField(
        source='get_quality_status_display',
        read_only=True
    )

    inspector_name = serializers.CharField(
        source='quality_inspector.username',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = ProductionBatch
        fields = [
            "id",
            "batch_number",
            "quality_status",
            "quality_status_display",
            "product_name",
            "quantity_produced",
            "produced_at",
            "operator_name",
            "order_id",
            "components",
            "created_at",
            # Поля контроля качества
            "quantity_accepted",
            "quantity_defective",
            "defect_reason",
            "quality_comment",
            "quality_checked_at",
            "quality_inspector",
            "inspector_name",
        ]

class QualityCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionBatch
        fields = [
            "quantity_accepted",
            "quantity_defective",
            "defect_reason",
            "quality_comment",
        ]

    def validate(self, data):
        qa = data.get("quantity_accepted")
        qd = data.get("quantity_defective")

        if qa is None or qd is None:
            raise serializers.ValidationError(
                "Нужно указать принято и брак"
            )

        if qa < 0 or qd < 0:
            raise serializers.ValidationError(
                "Количество не может быть отрицательным"
            )

        # УБРАЛ ВСЕ ОГРАНИЧЕНИЯ - можно любые значения
        # проверка на ноль тоже убираем

        if qd > 0 and not data.get("defect_reason"):
            raise serializers.ValidationError({
                "defect_reason": "Обязательное поле при наличии брака"
            })

        return data

    def update(self, instance, validated_data):
        request = self.context.get("request")

        instance.quantity_accepted = validated_data["quantity_accepted"]
        instance.quantity_defective = validated_data["quantity_defective"]
        instance.defect_reason = validated_data.get("defect_reason", "")
        instance.quality_comment = validated_data.get("quality_comment", "")

        # 🎯 ФИНАЛЬНЫЙ СТАТУС
        if instance.quantity_defective == Decimal("0"):
            instance.quality_status = "passed"
        elif instance.quantity_accepted == Decimal("0"):
            instance.quality_status = "failed"
        else:
            instance.quality_status = "passed_with_defects"

        instance.quality_inspector = request.user
        instance.quality_checked_at = timezone.now()

        # УБРАЛ СПИСАНИЕ В ЭТОМ МЕСТЕ
        # Теперь только меняем статус
        instance.save()

        return instance