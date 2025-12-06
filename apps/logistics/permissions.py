from rest_framework.permissions import BasePermission


class IsLogisticsUser(BasePermission):
    """
    Допускаем:
    - system_role: owner / admin
    - либо бизнес-роль с именем 'logistics_manager'
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        # системные роли
        if getattr(user, "system_role", None) in ["owner", "admin"]:
            return True

        # бизнес-роль из модели Role
        role = getattr(user, "role", None)
        if role and role.name == "logistics_manager":
            return True

        return False
