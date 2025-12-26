from django.urls import path
from .views import (
    RawMaterialListCreateView,
    RawMaterialDetailView,
    RawMaterialReceiptListCreateView,
    RawMaterialBatchesBalancesView,
    RecipeListCreateView,
    RecipeDetailView

)

urlpatterns = [
    path("materials/", RawMaterialListCreateView.as_view()),
    path("materials/<int:pk>/", RawMaterialDetailView.as_view()),
    path("receipts/", RawMaterialReceiptListCreateView.as_view()),
    path("balances/batches/", RawMaterialBatchesBalancesView.as_view()),
    path("recipes/", RecipeListCreateView.as_view()),
    path("recipes/<int:pk>/", RecipeDetailView.as_view()),
]
