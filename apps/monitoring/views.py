from rest_framework import viewsets, filters
from .models import ProductionLine
from .serializers import ProductionLineSerializer


class ProductionLineViewSet(viewsets.ModelViewSet):
    """
    Производственный контроль линий
    """
    queryset = ProductionLine.objects.all().order_by("code")
    serializer_class = ProductionLineSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["code", "name"]
