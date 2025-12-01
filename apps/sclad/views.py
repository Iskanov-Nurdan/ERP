from django.utils import timezone
from django.db.models import Sum
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import RawMaterial, RawMaterialMovement, FinishedProduct
from .serializers import (
    RawMaterialSerializer,
    RawMaterialMovementSerializer,
    FinishedProductSerializer,
)
from .permissions import IsWarehouseStaff



class RawMaterialListCreateView(generics.ListCreateAPIView):
    queryset = RawMaterial.objects.all()
    serializer_class = RawMaterialSerializer
    permission_classes = [IsWarehouseStaff]


class RawMaterialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RawMaterial.objects.all()
    serializer_class = RawMaterialSerializer
    permission_classes = [IsWarehouseStaff]


class RawMaterialMovementListCreateView(generics.ListCreateAPIView):

    queryset = RawMaterialMovement.objects.select_related("material", "performed_by")
    serializer_class = RawMaterialMovementSerializer
    permission_classes = [IsWarehouseStaff]

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)


class RawMaterialMovementListByMaterialView(generics.ListAPIView):

    serializer_class = RawMaterialMovementSerializer
    permission_classes = [IsWarehouseStaff]

    def get_queryset(self):
        material_id = self.kwargs["pk"]
        return RawMaterialMovement.objects.filter(material_id=material_id)


class RawMaterialMonthlyReportView(APIView):
 
    permission_classes = [IsWarehouseStaff]

    def get(self, request):
        now = timezone.now()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        qs = RawMaterialMovement.objects.filter(created_at__gte=start)

        incoming = qs.filter(operation_type="in").aggregate(
            total=Sum("quantity")
        )["total"] or 0

        outgoing = qs.filter(operation_type="out").aggregate(
            total=Sum("quantity")
        )["total"] or 0

        return Response(
            {
                "period": start.strftime("%Y-%m"),
                "total_incoming": str(incoming),
                "total_outgoing": str(outgoing),
            }
        )



class FinishedProductListCreateView(generics.ListCreateAPIView):
    queryset = FinishedProduct.objects.all()
    serializer_class = FinishedProductSerializer
    permission_classes = [IsWarehouseStaff]


class FinishedProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FinishedProduct.objects.all()
    serializer_class = FinishedProductSerializer
    permission_classes = [IsWarehouseStaff]
