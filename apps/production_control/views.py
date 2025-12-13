from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import ProductionLine
from .serializers import ProductionLineSerializer
from .permissions import IsProductionControlUser


class ProductionLineListCreateView(generics.ListCreateAPIView):
    queryset = ProductionLine.objects.all()
    serializer_class = ProductionLineSerializer
    permission_classes = [IsAuthenticated, IsProductionControlUser]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["identifier", "name", "status"]
    ordering_fields = ["speed_percent", "output_per_shift", "updated_at"]
    ordering = ["identifier"]

    def get_queryset(self):
        qs = super().get_queryset()
        status_ = self.request.query_params.get("status")
        if status_:
            qs = qs.filter(status=status_)
        return qs


class ProductionLineRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductionLine.objects.all()
    serializer_class = ProductionLineSerializer
    permission_classes = [IsAuthenticated, IsProductionControlUser]


class ProductionLineStatusView(APIView):
    permission_classes = [IsAuthenticated, IsProductionControlUser]

    def get(self, request, pk: int):
        try:
            line = ProductionLine.objects.get(pk=pk)
        except ProductionLine.DoesNotExist:
            return Response({"detail": "Линия не найдена."}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "id": line.id,
                "identifier": line.identifier,
                "name": line.name,
                "status": line.status,
                "status_label": line.get_status_display(),
                "speed_percent": line.speed_percent,
                "output_per_shift": line.output_per_shift,
                "updated_at": line.updated_at,
            },
            status=status.HTTP_200_OK,
        )


class ProductionLineStartView(APIView):
    permission_classes = [IsAuthenticated, IsProductionControlUser]

    def post(self, request, pk: int):
        try:
            line = ProductionLine.objects.get(pk=pk)
        except ProductionLine.DoesNotExist:
            return Response({"detail": "Линия не найдена."}, status=status.HTTP_404_NOT_FOUND)

        line.status = ProductionLine.Status.RUNNING
        line.save(update_fields=["status", "updated_at"])
        return Response(ProductionLineSerializer(line).data, status=status.HTTP_200_OK)


class ProductionLineStopView(APIView):
    permission_classes = [IsAuthenticated, IsProductionControlUser]

    def post(self, request, pk: int):
        try:
            line = ProductionLine.objects.get(pk=pk)
        except ProductionLine.DoesNotExist:
            return Response({"detail": "Линия не найдена."}, status=status.HTTP_404_NOT_FOUND)

        line.status = ProductionLine.Status.STOPPED
        line.speed_percent = 0
        line.save(update_fields=["status", "speed_percent", "updated_at"])
        return Response(ProductionLineSerializer(line).data, status=status.HTTP_200_OK)


class ProductionLineHistoryView(APIView):
    """
    MVP-версия: возвращаем просто последние обновления (без отдельной таблицы истории).
    Если хочешь настоящую историю — добавим ProductionLineEvent.
    """
    permission_classes = [IsAuthenticated, IsProductionControlUser]

    def get(self, request, pk: int):
        try:
            line = ProductionLine.objects.get(pk=pk)
        except ProductionLine.DoesNotExist:
            return Response({"detail": "Линия не найдена."}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "id": line.id,
                "identifier": line.identifier,
                "last_maintenance_at": line.last_maintenance_at,
                "updated_at": line.updated_at,
                "note": "MVP history: отдельной истории событий пока нет.",
            },
            status=status.HTTP_200_OK,
        )
