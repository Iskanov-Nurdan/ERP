from django.urls import path
from .views import (
    WarehouseListCreateView, WarehouseDetailView,
    MaterialListCreateView, MaterialDetailView,
    MaterialStockListView, MaterialStockAdjustView,
    MaterialMovementListView,
    MaterialReservationListCreateView, MaterialReservationDetailView,
)

urlpatterns = [
    # Warehouses
    path("warehouses/", WarehouseListCreateView.as_view(), name="warehouse-list"),
    path("warehouses/<int:pk>/", WarehouseDetailView.as_view(), name="warehouse-detail"),

    # Materials
    path("materials/", MaterialListCreateView.as_view(), name="material-list"),
    path("materials/<int:pk>/", MaterialDetailView.as_view(), name="material-detail"),

    # Stock
    path("stock/", MaterialStockListView.as_view(), name="material-stock-list"),
    path("stock/adjust/", MaterialStockAdjustView.as_view(), name="material-stock-adjust"),

    # Movements
    path("movements/", MaterialMovementListView.as_view(), name="material-movement-list"),

    # Reservations
    path("reservations/", MaterialReservationListCreateView.as_view(), name="material-reservation-list"),
    path("reservations/<int:pk>/", MaterialReservationDetailView.as_view(), name="material-reservation-detail"),
]
