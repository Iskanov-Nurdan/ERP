from django.urls import path
from .views import (
    RawMaterialListCreateView,
    RawMaterialDetailView,
    RawMaterialReceiptListCreateView,
    RawMaterialBatchesBalancesView,
    RecipeListCreateView,
    RecipeDetailView,
    # 👇 ДОБАВЬ ЭТИ ИМПОРТЫ
    ProductionBatchesForAcceptanceView,
    FinishedProductBatchCreateView,
    FinishedProductBatchListView,
    FinishedProductBalanceView
)

urlpatterns = [
    path("materials/", RawMaterialListCreateView.as_view()),
    path("materials/<int:pk>/", RawMaterialDetailView.as_view()),
    path("receipts/", RawMaterialReceiptListCreateView.as_view()),
    path("balances/batches/", RawMaterialBatchesBalancesView.as_view()),
    path("recipes/", RecipeListCreateView.as_view()),
    path("recipes/<int:pk>/", RecipeDetailView.as_view()),


    path('finished-products/pending/', ProductionBatchesForAcceptanceView.as_view(), name='finished-products-pending'),
    path('finished-products/accept/', FinishedProductBatchCreateView.as_view(), name='finished-products-accept'),
    path('finished-products/list/', FinishedProductBatchListView.as_view(), name='finished-products-list'),
    path('finished-products/balance/', FinishedProductBalanceView.as_view(), name='finished-products-balance'),
]

