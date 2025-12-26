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
    search_fields = ["name"]
    ordering_fields = ["name", "created_at", "updated_at"]
    ordering = ["name"]


class ProductionLineRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductionLine.objects.all()
    serializer_class = ProductionLineSerializer
    permission_classes = [IsAuthenticated, IsProductionControlUser]
