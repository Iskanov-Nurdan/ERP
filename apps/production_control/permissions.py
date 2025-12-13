from rest_framework.permissions import BasePermission


class IsProductionControlUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if getattr(user, "system_role", None) in ["owner", "admin"]:
            return True

        role = getattr(user, "role", None)
        if role and getattr(role, "name", None) in ["production_operator", "production_worker"]:
            return True

        return False
