from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import ProductionOrder
from .serializers import (
    ProductionOrderSerializer,
    ProductionOrderCompleteSerializer,
    ProductionOrderRejectSerializer,
)
from .permissions import IsProductionStaff


class ProductionOrderListCreateView(generics.ListCreateAPIView):
    queryset = ProductionOrder.objects.all()
    serializer_class = ProductionOrderSerializer
    permission_classes = [IsProductionStaff]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProductionOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductionOrder.objects.all()
    serializer_class = ProductionOrderSerializer
    permission_classes = [IsProductionStaff]


class ProductionOrderStartView(APIView):
    permission_classes = [IsProductionStaff]

    def post(self, request, pk: int):
        try:
            order = ProductionOrder.objects.get(pk=pk)
        except ProductionOrder.DoesNotExist:
            return Response({"detail": "Заказ не найден."}, status=status.HTTP_404_NOT_FOUND)

        if order.status in [ProductionOrder.Status.DONE, ProductionOrder.Status.REJECTED]:
            return Response({"detail": "Нельзя запустить завершённый/отбракованный заказ."}, status=400)

        order.status = ProductionOrder.Status.IN_PROGRESS
        if not order.started_at:
            order.started_at = timezone.now()

        # если линия есть — считаем её running
        if order.production_line:
            line = order.production_line
            line.status = line.Status.RUNNING
            line.monitored_by = request.user
            line.save(update_fields=["status", "monitored_by", "updated_at"])

        order.save(update_fields=["status", "started_at", "updated_at"])
        return Response(ProductionOrderSerializer(order).data, status=200)


class ProductionOrderCompleteView(APIView):
    permission_classes = [IsProductionStaff]

    def post(self, request, pk: int):
        try:
            order = ProductionOrder.objects.get(pk=pk)
        except ProductionOrder.DoesNotExist:
            return Response({"detail": "Заказ не найден."}, status=status.HTTP_404_NOT_FOUND)

        if order.status in [ProductionOrder.Status.DONE, ProductionOrder.Status.REJECTED]:
            return Response({"detail": "Заказ уже закрыт."}, status=400)

        s = ProductionOrderCompleteSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        produced = s.validated_data["produced_quantity"]
        defect = s.validated_data.get("defect_quantity", 0)
        notes = s.validated_data.get("notes", "")

        order.produced_quantity = produced
        order.defect_quantity = defect
        order.status = ProductionOrder.Status.DONE
        order.completed_at = timezone.now()
        if notes:
            order.comment = (order.comment + "\n" + notes).strip()

        # обновляем линию (выпуск за смену)
        if order.production_line:
            line = order.production_line
            # MVP: просто плюсуем по округлению (или делай свою логику)
            line.output_per_shift = int(line.output_per_shift + float(produced))
            line.save(update_fields=["output_per_shift", "updated_at"])

        order.save(update_fields=["produced_quantity", "defect_quantity", "status", "completed_at", "comment", "updated_at"])
        return Response(ProductionOrderSerializer(order).data, status=200)


class ProductionOrderRejectView(APIView):
    permission_classes = [IsProductionStaff]

    def post(self, request, pk: int):
        try:
            order = ProductionOrder.objects.get(pk=pk)
        except ProductionOrder.DoesNotExist:
            return Response({"detail": "Заказ не найден."}, status=status.HTTP_404_NOT_FOUND)

        if order.status in [ProductionOrder.Status.DONE, ProductionOrder.Status.REJECTED]:
            return Response({"detail": "Заказ уже закрыт."}, status=400)

        s = ProductionOrderRejectSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        defect_weight = s.validated_data["defect_weight"]
        reason = s.validated_data.get("reason", "")

        order.defect_quantity = defect_weight
        order.status = ProductionOrder.Status.REJECTED
        order.completed_at = timezone.now()
        if reason:
            order.comment = (order.comment + "\n" + "REJECT: " + reason).strip()

        if order.production_line:
            line = order.production_line
            # MVP: считаем брак тоже "в выпуск" не добавляем, только фиксируем что линия работала
            line.save(update_fields=["updated_at"])

        order.save(update_fields=["defect_quantity", "status", "completed_at", "comment", "updated_at"])
        return Response(ProductionOrderSerializer(order).data, status=200)


class ProductionOrderMoveNextView(APIView):
    permission_classes = [IsProductionStaff]

    def post(self, request, pk: int):
        try:
            order = ProductionOrder.objects.get(pk=pk)
        except ProductionOrder.DoesNotExist:
            return Response({"detail": "Заказ не найден."}, status=status.HTTP_404_NOT_FOUND)

        if order.status in [ProductionOrder.Status.DONE, ProductionOrder.Status.REJECTED]:
            return Response({"detail": "Заказ уже закрыт."}, status=400)

        order.move_to_next_stage()
        order.save(update_fields=["current_stage", "status", "completed_at", "updated_at"])

        return Response(ProductionOrderSerializer(order).data, status=200)
