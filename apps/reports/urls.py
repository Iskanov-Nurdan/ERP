from django.urls import path
from .views import (
    RawMaterialReportView,
    ProductionPlanFactReportView,
    QualityReportView,
)

urlpatterns = [
    path("raw-material/", RawMaterialReportView.as_view(), name="report-raw-material"),
    path("production-plan-fact/", ProductionPlanFactReportView.as_view(),name="report-production-plan-fact"),
    path("quality/", QualityReportView.as_view(), name="report-quality"),
]
