from django.urls import path
from .views import (
    RawMaterialListCreateView,
    RawMaterialDetailView,
    RawMaterialMovementListCreateView,
    RawMaterialMovementListByMaterialView,
    RawMaterialMonthlyReportView,
    FinishedProductListCreateView,
    FinishedProductDetailView,
)

urlpatterns = [
    # --- сырьё ---
    path("raw-materials/", RawMaterialListCreateView.as_view(), name="raw-material-list"),
    path(
        "raw-materials/<int:pk>/",
        RawMaterialDetailView.as_view(),
        name="raw-material-detail",
    ),
    path(
        "raw-materials/movements/",
        RawMaterialMovementListCreateView.as_view(),
        name="raw-material-movements",
    ),
    path(
        "raw-materials/<int:pk>/movements/",
        RawMaterialMovementListByMaterialView.as_view(),
        name="raw-material-movements-by-material",
    ),
    path(
        "raw-materials/report/monthly/",
        RawMaterialMonthlyReportView.as_view(),
        name="raw-material-report-monthly",
    ),

    # --- готовая продукция ---
    path(
        "finished-products/",
        FinishedProductListCreateView.as_view(),
        name="finished-product-list",
    ),
    path(
        "finished-products/<int:pk>/",
        FinishedProductDetailView.as_view(),
        name="finished-product-detail",
    ),
]
