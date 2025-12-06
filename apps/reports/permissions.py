from rest_framework.permissions import BasePermission


class IsAdminReports(BasePermission):
    """
    Отчёты только для owner/admin.
    Если хочешь – разреши ещё кому-то.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        return getattr(user, "system_role", None) in ["owner", "admin"]
