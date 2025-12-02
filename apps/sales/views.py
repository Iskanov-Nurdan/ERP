from django.db.models import Sum
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import CustomerOrder
from .serializers import CustomerOrderSerializer
from .permissions import IsSalesStaff


class CustomerOrderListCreateView(generics.ListCreateAPIView):
    queryset = CustomerOrder.objects.all()
    serializer_class = CustomerOrderSerializer
    permission_classes = [IsSalesStaff]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CustomerOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomerOrder.objects.all()
    serializer_class = CustomerOrderSerializer
    permission_classes = [IsSalesStaff]


class CustomerOrderActiveSummaryView(APIView):
    permission_classes = [IsSalesStaff]

    def get(self, request):
        active_statuses = [
            CustomerOrder.Status.NEW,
            CustomerOrder.Status.IN_WORK,
            CustomerOrder.Status.CONFIRMED,
        ]
        qs = CustomerOrder.objects.filter(status__in=active_statuses)
        total = qs.aggregate(total=Sum("amount"))["total"] or 0
        return Response(
            {
                "total_active_amount": str(total),
                "active_orders_count": qs.count(),
            },
            status=status.HTTP_200_OK,
        )
