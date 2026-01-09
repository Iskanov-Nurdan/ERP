from rest_framework.permissions import BasePermission


class IsProductionControlUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if getattr(user, "system_role", None) in ["owner", "admin"]:
            return True

        role = getattr(user, "role", None)
        return bool(role and getattr(role, "name", None) in ["production_operator", "production_worker"])


class IsQualityControlUser(BasePermission):
    """Разрешение для пользователей ОТК (контроль качества)"""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if getattr(user, "system_role", None) in ["owner", "admin"]:
            return True

        role = getattr(user, "role", None)
        return bool(role and getattr(role, "name", None) in ["quality_inspector"])


class IsOrderManager(BasePermission):
    """Разрешение для менеджеров заказов"""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if getattr(user, "system_role", None) in ["owner", "admin"]:
            return True

        role = getattr(user, "role", None)
        return bool(role and getattr(role, "name", None) in ["order_manager", "production_operator"])


class IsWarehouseUser(BasePermission):
    """Разрешение для сотрудников склада"""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if getattr(user, "system_role", None) in ["owner", "admin"]:
            return True

        role = getattr(user, "role", None)
        return bool(role and getattr(role, "name", None) in ["warehouse_worker", "warehouse_manager"])


class IsRecipeManager(BasePermission):
    """Разрешение для управления рецептами"""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if getattr(user, "system_role", None) in ["owner", "admin"]:
            return True

        role = getattr(user, "role", None)
        return bool(role and getattr(role, "name", None) in ["technologist", "recipe_manager"])