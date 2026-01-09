from rest_framework import generics, permissions
from .models import ProductionOrder
from .serializers import (
    ProductionOrderCreateSerializer,
    ProductionOrderListSerializer
)


class ProductionOrderCreateView(generics.CreateAPIView):
    queryset = ProductionOrder.objects.all()
    serializer_class = ProductionOrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]



class ProductionOrderListView(generics.ListAPIView):
    serializer_class = ProductionOrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    queryset = ProductionOrder.objects.select_related(
        'recipe',
        'production_line',
        'created_by'
    ).prefetch_related(
        'recipe__items__material'
    )