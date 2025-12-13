from django.urls import path
from .views import (
    ProductionLineListCreateView,
    ProductionLineRetrieveUpdateDestroyView,
    ProductionLineStatusView,
    ProductionLineStartView,
    ProductionLineStopView,
    ProductionLineHistoryView,
)

urlpatterns = [
    path("lines/", ProductionLineListCreateView.as_view(), name="production-line-list-create"),
    path("lines/<int:pk>/", ProductionLineRetrieveUpdateDestroyView.as_view(), name="production-line-detail"),
    path("lines/<int:pk>/status/", ProductionLineStatusView.as_view(), name="production-line-status"),
    path("lines/<int:pk>/start/", ProductionLineStartView.as_view(), name="production-line-start"),
    path("lines/<int:pk>/stop/", ProductionLineStopView.as_view(), name="production-line-stop"),
    path("lines/<int:pk>/history/", ProductionLineHistoryView.as_view(), name="production-line-history"),
]
