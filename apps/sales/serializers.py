from rest_framework import serializers
from .models import CustomerOrder


class CustomerOrderSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(
        source="get_status_display", read_only=True
    )
    created_by_email = serializers.ReadOnlyField(source="created_by.email")

    class Meta:
        model = CustomerOrder
        fields = [
            "id",
            "client_name",
            "order_number",
            "amount",
            "status",
            "status_label",
            "comment",
            "created_by",
            "created_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_by",
            "created_by_email",
            "created_at",
            "updated_at",
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Сумма должна быть больше нуля.")
        return value
