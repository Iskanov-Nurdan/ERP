from rest_framework import serializers
from .models import QualityIssue


class QualityIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityIssue
        fields = [
            "id",
            "product_name",
            "defect_type",
            "lot",
            "severity",
            "corrective_actions",
            "detected_at",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "detected_at", "created_by", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        return super().create(validated_data)
