from decimal import Decimal
from django.apps import apps as django_apps
from django.db import transaction


def _get_model(app_label, model_name):
    return django_apps.get_model(app_label, model_name)


@transaction.atomic
def auto_consume_raw_materials(order, recipe_version, basis_kg, user=None):
    """
    Создаёт движения out по складу на основе рецептуры.
    basis_kg: сколько кг продукции списываем (обычно produced_quantity, иначе quantity_planned)

    Важно: чтобы не списывать два раза, мы ставим метку в comment.
    """
    if recipe_version is None:
        return

    basis_kg = Decimal(str(basis_kg or 0))
    if basis_kg <= 0:
        return

    Movement = _get_model("sclad", "RawMaterialMovement")

    marker = f"[AUTO_CONSUME] order={order.id} v={recipe_version.id}"

    # защита от двойного списания
    if hasattr(Movement, "comment"):
        if Movement.objects.filter(comment__icontains=marker).exists():
            return

    for item in recipe_version.items.select_related("material").all():
        qty = (Decimal(str(item.qty_per_kg)) * basis_kg)
        if qty <= 0:
            continue

        create_kwargs = {}

        # самое частое
        if hasattr(Movement, "material_id"):
            create_kwargs["material_id"] = item.material_id

        if hasattr(Movement, "quantity"):
            create_kwargs["quantity"] = qty

        if hasattr(Movement, "operation_type"):
            create_kwargs["operation_type"] = "out"

        if hasattr(Movement, "comment"):
            create_kwargs["comment"] = f"{marker} | {item.material.name} -{qty}kg"

        if user and hasattr(Movement, "created_by_id"):
            create_kwargs["created_by_id"] = user.id

        # если вдруг есть поле order/production_order — аккуратно попробуем привязать
        for possible in ["order_id", "production_order_id"]:
            if hasattr(Movement, possible):
                create_kwargs[possible] = order.id

        Movement.objects.create(**create_kwargs)
