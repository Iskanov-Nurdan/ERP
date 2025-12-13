from rest_framework import serializers
from .models import ProductionLine


class ProductionLineSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ProductionLine
        fields = [
            "id",
            "identifier",
            "name",
            "status",
            "status_label",
            "speed_percent",
            "output_per_shift",
            "last_maintenance_at",
            "monitored_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "monitored_by", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["monitored_by"] = request.user
        return super().create(validated_data)
