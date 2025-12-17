from datetime import date, timedelta

from django.db.models import Sum, Count, Q
from django.utils.dateparse import parse_date

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .permissions import IsAdminReports
from .utils import get_model


class RawMaterialReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdminReports]

    def get(self, request):
        start_str = request.query_params.get("start")
        end_str = request.query_params.get("end")

        start = parse_date(start_str) if start_str else (date.today() - timedelta(days=30))
        end = parse_date(end_str) if end_str else date.today()

        Movement = get_model("sclad", "RawMaterialMovement")

        movements = Movement.objects.filter(
            created_at__date__gte=start,
            created_at__date__lte=end,
        )

        total_in = movements.filter(operation_type="in").aggregate(total=Sum("quantity"))["total"] or 0
        total_out = movements.filter(operation_type="out").aggregate(total=Sum("quantity"))["total"] or 0

        per_material = (
            movements
            .values("material_id", "material__name")
            .annotate(
                qty_in=Sum("quantity", filter=Q(operation_type="in")),
                qty_out=Sum("quantity", filter=Q(operation_type="out")),
            )
            .order_by("material__name")
        )

        materials_data = []
        for row in per_material:
            qty_in = row["qty_in"] or 0
            qty_out = row["qty_out"] or 0
            materials_data.append({
                "id": row["material_id"],
                "name": row["material__name"],
                "in": qty_in,
                "out": qty_out,
                "balance": qty_in - qty_out,
            })

        return Response({
            "period": {"start": start, "end": end},
            "total_in": total_in,
            "total_out": total_out,
            "materials": materials_data,
        })


class ProductionPlanFactReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdminReports]

    def get(self, request):
        start_str = request.query_params.get("start")
        end_str = request.query_params.get("end")

        start = parse_date(start_str) if start_str else (date.today() - timedelta(days=30))
        end = parse_date(end_str) if end_str else date.today()

        ProductionOrder = get_model("production", "ProductionOrder")

        qs = ProductionOrder.objects.filter(
            created_at__date__gte=start,
            created_at__date__lte=end,
        )

        agg = qs.aggregate(
            planned=Sum("quantity_planned"),
            produced=Sum("produced_quantity"),
        )

        planned = agg["planned"] or 0
        produced = agg["produced"] or 0

        return Response({
            "period": {"start": start, "end": end},
            "planned_total": planned,
            "produced_total": produced,
            "delta": produced - planned,
        })


class QualityReportView(APIView):
    """
    GET /api/reports/quality/?start=YYYY-MM-DD&end=YYYY-MM-DD
    """
    permission_classes = [IsAuthenticated, IsAdminReports]

    def get(self, request):
        start_str = request.query_params.get("start")
        end_str = request.query_params.get("end")

        start = parse_date(start_str) if start_str else (date.today() - timedelta(days=30))
        end = parse_date(end_str) if end_str else date.today()

        QualityIssue = get_model("quality", "QualityIssue")

        qs = QualityIssue.objects.filter(
            detected_at__date__gte=start,
            detected_at__date__lte=end,
        )

        by_severity = (
            qs.values("severity")
            .annotate(total=Count("id"))
            .order_by("severity")
        )

        by_product = (
            qs.values("product_name")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        return Response({
            "period": {"start": start, "end": end},
            "total_issues": qs.count(),
            "by_severity": list(by_severity),
            "by_product": list(by_product),
        })
