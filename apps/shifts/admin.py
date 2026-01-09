from django.contrib import admin
from .models import Shift


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "line",
        "manager",
        "status",
        "started_at",
        "ended_at",
    )
    list_filter = ("status", "line", "date")
    search_fields = ("line__name", "manager__username")
    readonly_fields = ("created_at", "ended_at")

    actions = ["close_shift"]

    def close_shift(self, request, queryset):
        """Action to close selected shifts."""
        updated = 0
        for shift in queryset.filter(status=Shift.STATUS_ACTIVE):
            shift.close()
            updated += 1
        self.message_user(request, f"{updated} смен(ы) успешно закрыты.")
    close_shift.short_description = "Закрыть выбранные смены"
from django.contrib import admin

# Register your models here.
