from rest_framework import serializers
from .models import ProductionLine


class ProductionLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionLine
        fields = "__all__"
