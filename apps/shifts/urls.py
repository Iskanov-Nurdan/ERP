from django.urls import path
from .views import (
    OpenShiftView,
    CloseShiftView,
    ActiveShiftListView,
    ShiftHistoryListView,
)

urlpatterns = [
    path("shifts/open/", OpenShiftView.as_view()),
    path("shifts/<int:pk>/close/", CloseShiftView.as_view()),
    path("shifts/active/", ActiveShiftListView.as_view()),
    path("shifts/history/", ShiftHistoryListView.as_view()),
]
