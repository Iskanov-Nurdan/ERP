from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView,
    UsersListView,
    RoleCreateView,
    RoleListView,
    UserDetailView,
    UserDeleteView,
    MeView
)

urlpatterns = [

    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    path("users/", UsersListView.as_view(), name="users-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user-delete"),
    path("register/", RegisterView.as_view(), name="user-register"),

    path("roles/", RoleListView.as_view(), name="roles-list"),
    path("roles/create/", RoleCreateView.as_view(), name="roles-create"),

    path("me/", MeView.as_view(), name="user-me"),
]
