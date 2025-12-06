from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated

from .models import Shipment
from .serializers import ShipmentSerializer
from .permissions import IsLogisticsUser


class ShipmentListCreateView(generics.ListCreateAPIView):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated, IsLogisticsUser]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["client_name", "city", "status"]
    ordering_fields = ["created_at", "pallets_count", "eta_hours"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        status_ = self.request.query_params.get("status")
        city = self.request.query_params.get("city")

        if status_:
            qs = qs.filter(status=status_)
        if city:
            qs = qs.filter(city__icontains=city)

        return qs


class ShipmentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated, IsLogisticsUser]
