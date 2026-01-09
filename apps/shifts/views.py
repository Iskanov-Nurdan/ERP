from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from .models import Shift, ProductionLine
from .serializers import ShiftSerializer, ShiftOpenSerializer


class OpenShiftView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ShiftOpenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        line = ProductionLine.objects.get(id=serializer.validated_data["line"])

        shift = Shift.objects.create(
            date=timezone.now().date(),          # ✅ автоматически
            line=line,
            manager=request.user,                # ✅ автоматически
            started_at=timezone.now(),            # ✅ автоматически
            status=Shift.STATUS_ACTIVE,
        )

        return Response(
            ShiftSerializer(shift).data,
            status=status.HTTP_201_CREATED,
        )


class CloseShiftView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        shift = Shift.objects.filter(
            id=pk,
            status=Shift.STATUS_ACTIVE,
        ).first()

        if not shift:
            return Response(
                {"detail": "Активная смена не найдена"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        shift.close()

        return Response(
            ShiftSerializer(shift).data,
            status=status.HTTP_200_OK,
        )


class ActiveShiftListView(ListAPIView):
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Shift.objects.filter(
            status=Shift.STATUS_ACTIVE
        ).select_related("line", "manager")


class ShiftHistoryListView(ListAPIView):
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Shift.objects.filter(
            status=Shift.STATUS_CLOSED
        ).select_related("line", "manager").order_by("-ended_at")
