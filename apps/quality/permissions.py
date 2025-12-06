from rest_framework.permissions import BasePermission


class IsQualityUser(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if getattr(user, "system_role", None) in ["owner", "admin"]:
            return True

        role = getattr(user, "role", None)
        if role and role.name == "quality_control":
            return True

        return False
