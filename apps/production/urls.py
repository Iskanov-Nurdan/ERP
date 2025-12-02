from django.urls import path
from .views import (
    ProductionOrderListCreateView,
    ProductionOrderDetailView,
    ProductionOrderMoveNextView,
)

urlpatterns = [
    path("orders/",ProductionOrderListCreateView.as_view(),name="production-order-list"),
    path("orders/<int:pk>/",ProductionOrderDetailView.as_view(),name="production-order-detail"),
    path("orders/<int:pk>/move-next/",ProductionOrderMoveNextView.as_view(),name="production-order-move-next"),
]
