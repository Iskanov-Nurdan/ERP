from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UsersListView, UserDetailView, UserDeleteView, MeView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", TokenObtainPairView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),

    path("users/", UsersListView.as_view()),
    path("users/<int:pk>/", UserDetailView.as_view()),
    path("users/<int:pk>/delete/", UserDeleteView.as_view()),
    path("me/", MeView.as_view(), name="user-me"),
]
