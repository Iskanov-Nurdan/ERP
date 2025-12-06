from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated

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
