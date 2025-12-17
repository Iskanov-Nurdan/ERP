from django.urls import path
from .views import (
    RecipeListCreateView,
    RecipeDetailView,
    RecipeVersionListCreateView,
    RecipeVersionDetailView,
    RecipeVersionActivateView,
)

urlpatterns = [
    path("recipes/", RecipeListCreateView.as_view(), name="recipes-list"),
    path("recipes/<int:pk>/", RecipeDetailView.as_view(), name="recipes-detail"),

    path("recipes/<int:recipe_id>/versions/", RecipeVersionListCreateView.as_view(), name="recipe-versions"),
    path("versions/<int:pk>/", RecipeVersionDetailView.as_view(), name="recipe-version-detail"),
    path("versions/<int:pk>/activate/", RecipeVersionActivateView.as_view(), name="recipe-version-activate"),
]
