
from django.db import models
from django.db import transaction
from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Warehouse, Material, MaterialStock, MaterialMovement, MaterialReservation
from .serializers import (
    WarehouseSerializer,
    MaterialSerializer,
    MaterialStockSerializer,
    MaterialMovementSerializer,
    MaterialReservationSerializer,
)
from .permissions import IsWarehouseStaff


# ===== Warehouses =====
class WarehouseListCreateView(generics.ListCreateAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated, IsWarehouseStaff]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "address"]


class WarehouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated, IsWarehouseStaff]


# ===== Materials =====
class MaterialListCreateView(generics.ListCreateAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, IsWarehouseStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code", "supplier"]
    ordering_fields = ["name", "code", "updated_at"]
    ordering = ["name"]


class MaterialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, IsWarehouseStaff]


# ===== Stocks =====
class MaterialStockListView(generics.ListAPIView):
    queryset = MaterialStock.objects.select_related("material", "warehouse").all()
    serializer_class = MaterialStockSerializer
    permission_classes = [IsAuthenticated, IsWarehouseStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["material__name", "material__code", "warehouse__name"]
    ordering_fields = ["quantity", "updated_at"]
    ordering = ["warehouse__name", "material__name"]

    def get_queryset(self):
        qs = super().get_queryset()
        material_id = self.request.query_params.get("material_id")
        warehouse_id = self.request.query_params.get("warehouse_id")
        low_stock = self.request.query_params.get("low_stock")

        if material_id:
            qs = qs.filter(material_id=material_id)
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)

        if low_stock == "true":
            # quantity < min_stock
            qs = qs.filter(quantity__lt=models.F("material__min_stock"))

        return qs


class MaterialStockAdjustView(APIView):
    """
    POST /api/warehouse/stock/adjust/
    body: { material, warehouse, movement_type: in|out|adjustment, quantity, notes }
    """
    permission_classes = [IsAuthenticated, IsWarehouseStaff]

    @transaction.atomic
    def post(self, request):
        material_id = request.data.get("material")
        warehouse_id = request.data.get("warehouse")
        movement_type = request.data.get("movement_type")
        quantity = request.data.get("quantity")
        notes = request.data.get("notes", "")

        if not material_id or not warehouse_id or not movement_type or quantity is None:
            return Response({"detail": "material, warehouse, movement_type, quantity обязательны."}, status=400)

        try:
            qty = float(quantity)
        except Exception:
            return Response({"detail": "quantity должно быть числом."}, status=400)

        if qty <= 0:
            return Response({"detail": "quantity должно быть > 0."}, status=400)

        material = Material.objects.get(pk=material_id)
        warehouse = Warehouse.objects.get(pk=warehouse_id)

        stock, _ = MaterialStock.objects.get_or_create(material=material, warehouse=warehouse)

        if movement_type == MaterialMovement.Type.IN:
            stock.quantity = stock.quantity + qty
            move = MaterialMovement.objects.create(
                movement_type=MaterialMovement.Type.IN,
                material=material,
                from_warehouse=None,
                to_warehouse=warehouse,
                quantity=qty,
                notes=notes,
                created_by=request.user,
            )

        elif movement_type == MaterialMovement.Type.OUT:
            if float(stock.quantity) < qty:
                return Response({"detail": "Недостаточно остатка на складе."}, status=400)
            stock.quantity = stock.quantity - qty
            move = MaterialMovement.objects.create(
                movement_type=MaterialMovement.Type.OUT,
                material=material,
                from_warehouse=warehouse,
                to_warehouse=None,
                quantity=qty,
                notes=notes,
                created_by=request.user,
            )

        elif movement_type == MaterialMovement.Type.ADJUSTMENT:
            # корректировка = выставить точное значение qty
            stock.quantity = qty
            move = MaterialMovement.objects.create(
                movement_type=MaterialMovement.Type.ADJUSTMENT,
                material=material,
                from_warehouse=warehouse,
                to_warehouse=warehouse,
                quantity=qty,
                notes=(notes or "Корректировка"),
                created_by=request.user,
            )
        else:
            return Response({"detail": "movement_type должен быть: in|out|adjustment."}, status=400)

        stock.save(update_fields=["quantity", "updated_at"])
        return Response(
            {
                "stock": MaterialStockSerializer(stock).data,
                "movement": MaterialMovementSerializer(move).data,
            },
            status=200,
        )


# ===== Movements =====
class MaterialMovementListView(generics.ListAPIView):
    queryset = MaterialMovement.objects.select_related("material", "from_warehouse", "to_warehouse", "created_by").all()
    serializer_class = MaterialMovementSerializer
    permission_classes = [IsAuthenticated, IsWarehouseStaff]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        mtype = self.request.query_params.get("type")
        material_id = self.request.query_params.get("material_id")
        warehouse_id = self.request.query_params.get("warehouse_id")

        if mtype:
            qs = qs.filter(movement_type=mtype)
        if material_id:
            qs = qs.filter(material_id=material_id)
        if warehouse_id:
            qs = qs.filter(models.Q(from_warehouse_id=warehouse_id) | models.Q(to_warehouse_id=warehouse_id))

        return qs


# ===== Reservations =====
class MaterialReservationListCreateView(generics.ListCreateAPIView):
    queryset = MaterialReservation.objects.select_related("material", "warehouse", "created_by").all()
    serializer_class = MaterialReservationSerializer
    permission_classes = [IsAuthenticated, IsWarehouseStaff]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class MaterialReservationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MaterialReservation.objects.select_related("material", "warehouse", "created_by").all()
    serializer_class = MaterialReservationSerializer
    permission_classes = [IsAuthenticated, IsWarehouseStaff]
