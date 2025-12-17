from django.urls import path
from .views import (
    ProductionOrderListCreateView,
    ProductionOrderDetailView,
    ProductionOrderStartView,
    ProductionOrderCompleteView,
    ProductionOrderRejectView,
    ProductionOrderMoveNextView,
    DowntimeListCreateView,
    DowntimeStopView,
)

urlpatterns = [
    path("orders/", ProductionOrderListCreateView.as_view(), name="production-order-list"),
    path("orders/<int:pk>/", ProductionOrderDetailView.as_view(), name="production-order-detail"),

    path("orders/<int:pk>/start/", ProductionOrderStartView.as_view(), name="production-order-start"),
    path("orders/<int:pk>/complete/", ProductionOrderCompleteView.as_view(), name="production-order-complete"),
    path("orders/<int:pk>/reject/", ProductionOrderRejectView.as_view(), name="production-order-reject"),

    path("orders/<int:pk>/move-next/", ProductionOrderMoveNextView.as_view(), name="production-order-move-next"),

    path("downtimes/", DowntimeListCreateView.as_view(), name="downtime-list-create"),
    path("downtimes/<int:pk>/stop/", DowntimeStopView.as_view(), name="downtime-stop"),

]