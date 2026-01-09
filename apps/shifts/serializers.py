from rest_framework import serializers
from django.utils import timezone
from .models import Shift
from apps.production_control.models import ProductionLine

class ShiftSerializer(serializers.ModelSerializer):
    line_name = serializers.CharField(source="line.name", read_only=True)
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Shift
        fields = '__all__'  # здесь уже есть manager из модели

    def get_duration_minutes(self, obj):
        if not obj.ended_at:
            return None
        delta = obj.ended_at - obj.started_at
        return int(delta.total_seconds() // 60)

class ShiftOpenSerializer(serializers.Serializer):
    line = serializers.IntegerField()

    def validate(self, attrs):
        line_id = attrs.get("line")
        if line_id is None:
            raise serializers.ValidationError("Линия обязательна")

        if Shift.objects.filter(
            line_id=line_id,
            status=Shift.STATUS_ACTIVE,
        ).exists():
            raise serializers.ValidationError(
                "На этой линии уже есть активная смена"
            )

        return attrs
