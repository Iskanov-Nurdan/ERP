from django.urls import path
from .views import (
    ShipmentListCreateView,
    ShipmentRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("shipments/", ShipmentListCreateView.as_view(), name="shipment-list-create"),
    path("shipments/<int:pk>/", ShipmentRetrieveUpdateDestroyView.as_view(),name="shipment-detail"),
]
