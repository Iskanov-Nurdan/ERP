from django.urls import path
from .views import (
    CustomerOrderListCreateView,
    CustomerOrderDetailView,
    CustomerOrderActiveSummaryView,
)

urlpatterns = [
    path("orders/",CustomerOrderListCreateView.as_view(),name="customer-order-list", ),
    path("orders/<int:pk>/", CustomerOrderDetailView.as_view(),name="customer-order-detail",),
    path("orders/summary/active/",CustomerOrderActiveSummaryView.as_view(),name="customer-order-active-summary",),
]
