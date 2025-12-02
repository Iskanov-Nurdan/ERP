from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import ProductionOrder
from .serializers import ProductionOrderSerializer
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


class ProductionOrderMoveNextView(APIView):

    permission_classes = [IsProductionStaff]

    def post(self, request, pk):
        try:
            order = ProductionOrder.objects.get(pk=pk)
        except ProductionOrder.DoesNotExist:
            return Response({"detail": "Заказ не найден."}, status=status.HTTP_404_NOT_FOUND)

        order.move_to_next_stage()
        order.save(update_fields=["current_stage", "status", "updated_at"])

        serializer = ProductionOrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
