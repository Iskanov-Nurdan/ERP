from django.urls import path
from .views import (
    ProductionLineListCreateView,
    ProductionLineRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("lines/", ProductionLineListCreateView.as_view(),name="production-line-list-create"),
    path("lines/<int:pk>/", ProductionLineRetrieveUpdateDestroyView.as_view(),name="production-line-detail"),
]
