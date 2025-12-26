from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView,
    UsersListView,
    RoleCreateView,
    RoleListView,
    RoleUpdateView,
    RoleDeleteView,
    UserDetailView,
    UserDeleteView,
    UserUpdateView,
    MeView,
    LoginView,
)

urlpatterns = [

    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    path("users/", UsersListView.as_view(), name="users-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user-delete"),
    path("register/", RegisterView.as_view(), name="user-register"),
    path("users/<int:pk>/update/", UserUpdateView.as_view(), name="user-update"),

    path("roles/", RoleListView.as_view(), name="roles-list"),
    path("roles/create/", RoleCreateView.as_view(), name="roles-create"),
    path("roles/<int:pk>/update/", RoleUpdateView.as_view(), name="roles-update"),
    path("roles/<int:pk>/delete/", RoleDeleteView.as_view(), name="roles-delete"),

    path("me/", MeView.as_view(), name="user-me"),

    path("login/", LoginView.as_view(), name="login"),

]
