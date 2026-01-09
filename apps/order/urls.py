from django.urls import path
from .views import (
    ProductionOrderCreateView,
    ProductionOrderListView,
)

urlpatterns = [
    path('', ProductionOrderListView.as_view(), name='production-order-list'),
    path('create/', ProductionOrderCreateView.as_view(), name='production-order-create'),
]
