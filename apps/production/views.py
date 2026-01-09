from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum
from django.db.models.functions import Coalesce
from decimal import Decimal
import uuid

from .models import ProductionBatch, ProductionComponent
from apps.sclad.models import RawMaterialReceipt, RawMaterialMovement
from .serializers import (
    ProductionBatchCreateSerializer,
    ProductionBatchListSerializer,
    ProductionBatchDetailSerializer,
    QualityCheckSerializer,
)
from .permissions import IsProductionControlUser, IsQualityControlUser  # Используем ваши классы
from apps.order.models import ProductionOrder


class ProductionBatchCreateView(generics.CreateAPIView):
    queryset = ProductionBatch.objects.all()
    serializer_class = ProductionBatchCreateSerializer
    permission_classes = [IsAuthenticated, IsProductionControlUser]


class ProductionBatchListView(generics.ListAPIView):
    queryset = (
        ProductionBatch.objects
        .select_related('operator', 'order')
        .order_by('-produced_at')
    )
    serializer_class = ProductionBatchListSerializer
    permission_classes = [IsAuthenticated, IsProductionControlUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        quality_status = self.request.query_params.get('quality_status')
        if quality_status:
            queryset = queryset.filter(quality_status=quality_status)
        return queryset


class ProductionBatchDetailView(generics.RetrieveAPIView):
    queryset = ProductionBatch.objects.all()
    serializer_class = ProductionBatchDetailSerializer
    permission_classes = [IsAuthenticated, IsProductionControlUser]
    lookup_field = 'id'


class ProductionTraceView(APIView):
    permission_classes = [IsAuthenticated, IsProductionControlUser]

    def get(self, request, id):
        try:
            batch_id = uuid.UUID(str(id))
            batch = ProductionBatch.objects.get(id=batch_id)
        except (ValueError, ProductionBatch.DoesNotExist):
            return Response(
                {"error": "Партия производства не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductionBatchDetailSerializer(batch)
        return Response(serializer.data)


# Новые классы для контроля качества

class ProductionBatchPendingQualityView(generics.ListAPIView):
    """Список партий, ожидающих проверки ОТК"""
    queryset = (
        ProductionBatch.objects
        .select_related('operator', 'order')
        .filter(quality_status='pending')
        .order_by('-produced_at')
    )
    serializer_class = ProductionBatchListSerializer
    permission_classes = [IsAuthenticated, IsQualityControlUser]


class ProductionBatchQualityHistoryView(generics.ListAPIView):
    """История проверенных партий ОТК"""
    queryset = (
        ProductionBatch.objects
        .select_related('operator', 'order', 'quality_inspector')
        .exclude(quality_status='pending')
        .order_by('-quality_checked_at')
    )
    serializer_class = ProductionBatchDetailSerializer
    permission_classes = [IsAuthenticated, IsQualityControlUser]


class ProductionBatchQualityInfoView(generics.RetrieveAPIView):
    """Получить информацию о партии для проверки качества"""
    queryset = ProductionBatch.objects.all()
    serializer_class = ProductionBatchDetailSerializer
    permission_classes = [IsAuthenticated, IsQualityControlUser]
    lookup_field = 'id'


class ProductionBatchQualityCheckView(APIView):
    permission_classes = [IsAuthenticated, IsQualityControlUser]

    def post(self, request, id):
        try:
            batch = ProductionBatch.objects.get(id=id)
        except ProductionBatch.DoesNotExist:
            return Response(
                {"error": "Партия производства не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        if batch.quality_status != "pending":
            return Response(
                {"error": "Партия уже проверена"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = QualityCheckSerializer(
            batch,
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "id": str(batch.id),
                "quality_status": batch.quality_status,
                "quality_status_display": batch.get_quality_status_display(),
            },
            status=status.HTTP_200_OK
        )


class ProductionStockBalanceView(APIView):
    permission_classes = [IsAuthenticated, IsProductionControlUser]

    def get(self, request):
        receipts = RawMaterialReceipt.objects.select_related("material").all()
        result = []

        for receipt in receipts:
            in_qty = RawMaterialMovement.objects.filter(
                material_id=receipt.material_id,
                receipt_id=receipt.id,
                operation_type=RawMaterialMovement.Operation.IN_
            ).aggregate(total=Coalesce(Sum('quantity'), Decimal('0')))['total']

            out_qty = RawMaterialMovement.objects.filter(
                material_id=receipt.material_id,
                receipt_id=receipt.id,
                operation_type=RawMaterialMovement.Operation.OUT
            ).aggregate(total=Coalesce(Sum('quantity'), Decimal('0')))['total']

            qty = float(in_qty - out_qty)

            if qty > 0:
                found = False
                for item in result:
                    if item["material_id"] == receipt.material_id:
                        item["total"] += qty
                        item["batches"].append({
                            "batch_number": receipt.batch_number or f"#{receipt.id}",
                            "qty": qty,
                            "date": receipt.date,
                            "supplier": receipt.supplier or "",
                            "receipt_id": receipt.id,
                            "unit_label": receipt.material.get_unit_display(),
                        })
                        found = True
                        break

                if not found:
                    result.append({
                        "material_id": receipt.material_id,
                        "material_name": receipt.material.name,
                        "unit_label": receipt.material.get_unit_display(),
                        "total": qty,
                        "batches": [{
                            "batch_number": receipt.batch_number or f"#{receipt.id}",
                            "qty": qty,
                            "date": receipt.date,
                            "supplier": receipt.supplier or "",
                            "receipt_id": receipt.id,
                            "unit_label": receipt.material.get_unit_display(),
                        }]
                    })

        return Response(result)