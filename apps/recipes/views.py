from django.db.models import Count, Max
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Recipe, RecipeVersion
from .serializers import RecipeSerializer, RecipeVersionSerializer
from .permissions import IsTechnologistOrAdmin


class RecipeListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsTechnologistOrAdmin]
    serializer_class = RecipeSerializer

    def get_queryset(self):
        return Recipe.objects.all().annotate(versions_count=Count("versions")).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsTechnologistOrAdmin]
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()


class RecipeVersionListCreateView(APIView):
    """
    GET  /api/recipes/recipes/<recipe_id>/versions/
    POST /api/recipes/recipes/<recipe_id>/versions/
    """
    permission_classes = [IsAuthenticated, IsTechnologistOrAdmin]

    def get(self, request, recipe_id: int):
        qs = RecipeVersion.objects.filter(recipe_id=recipe_id).prefetch_related("items")
        return Response(RecipeVersionSerializer(qs, many=True).data)

    def post(self, request, recipe_id: int):
        last_version = RecipeVersion.objects.filter(recipe_id=recipe_id).aggregate(m=Max("version"))["m"] or 0
        data = dict(request.data)
        data["recipe"] = recipe_id
        data.setdefault("version", last_version + 1)

        s = RecipeVersionSerializer(data=data, context={"request": request})
        s.is_valid(raise_exception=True)
        obj = s.save(created_by=request.user)

        return Response(RecipeVersionSerializer(obj).data, status=status.HTTP_201_CREATED)


class RecipeVersionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsTechnologistOrAdmin]
    serializer_class = RecipeVersionSerializer
    queryset = RecipeVersion.objects.all().prefetch_related("items")

    def perform_update(self, serializer):
        serializer.save()


class RecipeVersionActivateView(APIView):
    """
    POST /api/recipes/versions/<id>/activate/
    Делает эту версию активной, остальные версии этой рецептуры выключает.
    """
    permission_classes = [IsAuthenticated, IsTechnologistOrAdmin]

    def post(self, request, pk: int):
        try:
            v = RecipeVersion.objects.select_related("recipe").get(pk=pk)
        except RecipeVersion.DoesNotExist:
            return Response({"detail": "Версия не найдена."}, status=404)

        RecipeVersion.objects.filter(recipe=v.recipe).update(is_active=False)
        v.is_active = True
        v.save(update_fields=["is_active", "updated_at"])

        return Response(RecipeVersionSerializer(v).data, status=200)
