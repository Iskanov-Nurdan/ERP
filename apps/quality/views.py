from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated

from .models import QualityIssue
from .serializers import QualityIssueSerializer
from .permissions import IsQualityUser


class QualityIssueListCreateView(generics.ListCreateAPIView):
    queryset = QualityIssue.objects.all()
    serializer_class = QualityIssueSerializer
    permission_classes = [IsAuthenticated, IsQualityUser]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["product_name", "defect_type", "lot", "severity"]
    ordering_fields = ["created_at", "severity"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()

        product = self.request.query_params.get("product")
        lot = self.request.query_params.get("lot")
        severity = self.request.query_params.get("severity")

        if product:
            qs = qs.filter(product_name__icontains=product)
        if lot:
            qs = qs.filter(lot__icontains=lot)
        if severity:
            qs = qs.filter(severity=severity)

        return qs


class QualityIssueRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = QualityIssue.objects.all()
    serializer_class = QualityIssueSerializer
    permission_classes = [IsAuthenticated, IsQualityUser]
    queryset = QualityIssue.objects.all()
    serializer_class = QualityIssueSerializer
    permission_classes = [IsAuthenticated, IsQualityUser]
