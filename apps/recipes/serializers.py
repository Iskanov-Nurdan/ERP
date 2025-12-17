from rest_framework import serializers
from .models import Recipe, RecipeVersion, RecipeItem


class RecipeItemSerializer(serializers.ModelSerializer):
    material_name = serializers.ReadOnlyField(source="material.name")

    class Meta:
        model = RecipeItem
        fields = ["id", "material", "material_name", "qty_per_kg"]


class RecipeVersionSerializer(serializers.ModelSerializer):
    items = RecipeItemSerializer(many=True)
    created_by_email = serializers.ReadOnlyField(source="created_by.email")

    class Meta:
        model = RecipeVersion
        fields = [
            "id", "recipe", "version", "is_active", "note",
            "items", "created_by", "created_by_email",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_by", "created_by_email", "created_at", "updated_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        version = RecipeVersion.objects.create(**validated_data)
        for it in items_data:
            RecipeItem.objects.create(version=version, **it)
        return version

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)

        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for it in items_data:
                RecipeItem.objects.create(version=instance, **it)

        return instance


class RecipeSerializer(serializers.ModelSerializer):
    versions_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = ["id", "name", "product_name", "is_active", "versions_count", "created_by", "created_at", "updated_at"]
        read_only_fields = ["created_by", "created_at", "updated_at"]
