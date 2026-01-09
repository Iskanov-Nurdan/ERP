from django.urls import path
from . import views

urlpatterns = [
    # Существующие endpoints
    path('batches/', views.ProductionBatchCreateView.as_view(), name='production-batch-create'),
    path('batches/list/', views.ProductionBatchListView.as_view(), name='production-batch-list'),
    path('batches/<uuid:id>/', views.ProductionBatchDetailView.as_view(), name='production-batch-detail'),
    path('batches/<uuid:id>/trace/', views.ProductionTraceView.as_view(), name='production-trace'),
    path('stock-balance/', views.ProductionStockBalanceView.as_view(), name='production-stock-balance'),
    
    # Новые endpoints для контроля качества
    path('quality/pending/', views.ProductionBatchPendingQualityView.as_view(), name='quality-pending'),
    path('quality/history/', views.ProductionBatchQualityHistoryView.as_view(), name='quality-history'),
    path('batches/<uuid:id>/quality-check/', views.ProductionBatchQualityCheckView.as_view(), name='production-batch-quality-check'),
    path('batches/<uuid:id>/quality-info/', views.ProductionBatchQualityInfoView.as_view(), name='production-batch-quality-info'),
]