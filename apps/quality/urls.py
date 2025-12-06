from django.urls import path
from .views import (
    QualityIssueListCreateView,
    QualityIssueRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("issues/", QualityIssueListCreateView.as_view(), name="quality-issue-list-create"),
    path("issues/<int:pk>/", QualityIssueRetrieveUpdateDestroyView.as_view(),name="quality-issue-detail"),
]
