from rest_framework import serializers
from .models import ProductionOrder

from django.db.models import Sum  # ДОБАВЬТЕ ЭТОТ ИМПОРТ


class ProductionOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionOrder
        fields = (
            'id',
            'recipe',
            'production_line',
            'planned_quantity',
        )

    def create(self, validated_data):
        request = self.context['request']
        ProductionOrder.objects.filter(is_active=True).update(is_active=False)

        return ProductionOrder.objects.create(
            **validated_data,
            created_by=request.user,
            status=ProductionOrder.STATUS_CREATED,
            is_active=True
        )


class ProductionOrderListSerializer(serializers.ModelSerializer):
    recipe_name = serializers.CharField(
        source='recipe.name',
        read_only=True
    )
    production_line_name = serializers.CharField(
        source='production_line.name',
        read_only=True
    )
    created_by_name = serializers.CharField(
        source='created_by.username',
        read_only=True
    )

    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    production_batches = serializers.SerializerMethodField()
    total_produced = serializers.SerializerMethodField()
    quality_status = serializers.SerializerMethodField()

    materials = serializers.SerializerMethodField()

    class Meta:
        model = ProductionOrder
        fields = (
            'id',
            'recipe_name',
            'materials',
            'production_line_name',
            'planned_quantity',
            'status',
            'status_display',
            'created_by_name',
            'created_at',
            'is_active',
            'production_batches',
            'total_produced',
            'quality_status',
        )

    def get_materials(self, obj):
        recipe_items = obj.recipe.items.select_related('material')
        return [
            {
                "id": item.id,
                "material": item.material_id,
                "material_name": item.material.name,
                "quantity": str(item.quantity),
            }
            for item in recipe_items
        ]

    def get_production_batches(self, obj):
        try:
            batches = obj.production_batches.all()
            return [
                {
                    'id': str(batch.id),
                    'batch_number': batch.batch_number,
                    'quantity_produced': float(batch.quantity_produced),
                    'produced_at': batch.produced_at,
                    'quality_status': batch.quality_status,
                    'quality_status_display': batch.get_quality_status_display(),
                }
                for batch in batches
            ]
        except Exception:
            return []

    def get_total_produced(self, obj):
        try:
            total = obj.production_batches.filter(
                quality_status='passed'
            ).aggregate(total=Sum('quantity_produced'))['total']
            return float(total) if total else 0
        except Exception:
            return 0

    def get_quality_status(self, obj):
        try:
            batches = obj.production_batches.all()
            if not batches.exists():
                return 'Не начато'

            if all(b.quality_status == 'passed' for b in batches):
                return 'Все ОК'
            elif any(b.quality_status == 'failed' for b in batches):
                return 'Есть брак'
            else:
                return 'В процессе проверки'
        except Exception:
            return 'Неизвестно'

