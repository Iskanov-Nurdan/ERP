from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import (
    RawMaterial,
    RawMaterialReceipt,
    RawMaterialMovement,
    Recipe,
)
from .serializers import (
    RawMaterialSerializer,
    RawMaterialReceiptSerializer,
    RawMaterialBatchesBalanceSerializer,
    RecipeSerializer,
    RecipeWriteSerializer,   # ✅ ВОТ ЭТО ДОБАВЬ
)
from .permissions import IsOwnerOrAdmin


class RawMaterialListCreateView(generics.ListCreateAPIView):
    queryset = RawMaterial.objects.all()
    serializer_class = RawMaterialSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]


class RawMaterialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RawMaterial.objects.all()
    serializer_class = RawMaterialSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def destroy(self, request, *args, **kwargs):
        material = self.get_object()

        if material.receipts.exists():
            return Response(
                {"detail": "Сырьё с приходами удалить нельзя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if material.recipe_items.exists():
            return Response(
                {"detail": "Сырьё используется в рецептах"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)


class RawMaterialReceiptListCreateView(generics.ListCreateAPIView):
    queryset = RawMaterialReceipt.objects.select_related("material")
    serializer_class = RawMaterialReceiptSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    @transaction.atomic
    def perform_create(self, serializer):
        receipt = serializer.save()
        RawMaterialMovement.objects.create(
            material=receipt.material,
            operation_type=RawMaterialMovement.Operation.IN_,
            quantity=receipt.quantity,
            receipt=receipt,
        )


class RawMaterialBatchesBalancesView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get(self, request):
        receipts = (
            RawMaterialReceipt.objects.select_related("material")
            .annotate(
                out_qty=Coalesce(
                    Sum(
                        "movements__quantity",
                        filter=Q(movements__operation_type=RawMaterialMovement.Operation.OUT),
                    ),
                    Decimal("0"),
                )
            )
            .order_by("material__id", "date", "id")
        )

        grouped = {}

        for r in receipts:
            mid = r.material_id
            if mid not in grouped:
                grouped[mid] = {
                    "material_id": mid,
                    "material_name": r.material.name,
                    "unit_label": r.material.get_unit_display(),
                    "total": Decimal("0"),
                    "batches": [],
                }

            # баланс партии = приход - списание по этой партии
            qty = (r.quantity or Decimal("0")) - (r.out_qty or Decimal("0"))

            # если партия “ушла в ноль” — можно скрывать (по желанию)
            # if qty <= 0:
            #     continue

            batch_number = (r.batch_number or "").strip() or f"REC-{r.id}"

            grouped[mid]["batches"].append(
                {
                    "batch_number": batch_number,
                    "qty": qty,
                    "date": r.date,
                    "supplier": r.supplier or "",
                }
            )
            grouped[mid]["total"] += qty

        data = list(grouped.values())

        serializer = RawMaterialBatchesBalanceSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)# =======================
# РЕЦЕПТЫ
# =======================

class RecipeListCreateView(generics.ListCreateAPIView):
    queryset = Recipe.objects.prefetch_related("items__material")
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RecipeWriteSerializer
        return RecipeSerializer


class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.prefetch_related("items__material")
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return RecipeWriteSerializer
        return RecipeSerializer