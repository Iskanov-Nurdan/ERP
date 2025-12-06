from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.apps import apps


def safe_count(app_label, model_name, **filters):
    try:
        Model = apps.get_model(app_label, model_name)
    except LookupError:
        return 0

    try:
        return Model.objects.filter(**filters).count()
    except Exception:
        return 0


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # ---------------------------
        # 1. Остатки сырья (если есть модель RawMaterial)
        # ---------------------------
        raw_material_items = safe_count("sclad", "RawMaterial")

        # ---------------------------
        # 2. Активные заказы клиентов (твоя модель CustomerOrder)
        # ---------------------------
        active_orders = safe_count(
            "sales",
            "CustomerOrder",
            status__in=["new", "in_work", "confirmed"]
        )

        # ---------------------------
        # 3. Линии, которые работают
        # ---------------------------
        running_lines = safe_count(
            "production_control",
            "ProductionLine",
            status="running"
        )

        # ---------------------------
        # 4. Отгрузки, которые в пути
        # ---------------------------
        shipments_in_transit = safe_count(
            "logistics",
            "Shipment",
            status="in_transit"
        )

        # ---------------------------
        # 5. Несоответствия по качеству
        # ---------------------------
        quality_issues = safe_count(
            "quality",
            "QualityIssue"
        )

        return Response({
            "raw_material_items": raw_material_items,
            "active_orders": active_orders,
            "running_lines": running_lines,
            "shipments_in_transit": shipments_in_transit,
            "quality_issues": quality_issues,
        })
