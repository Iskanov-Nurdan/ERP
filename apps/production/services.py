from decimal import Decimal

def try_auto_writeoff_raw_materials(order):
    """
    Автосписание сырья по активной рецептуре.
    Не ломает систему: если моделей склада нет или рецептур нет — просто return.
    """
    try:
        from apps.recipes.models import Recipe
    except Exception:
        return

    recipe = Recipe.objects.filter(product_name=order.product_name, is_active=True).prefetch_related("items").first()
    if not recipe:
        return

    produced = order.produced_quantity or Decimal("0")
    if produced <= 0:
        return

    # Попытайся подключиться к твоим складским моделям
    MovementModel = None
    try:
        # если у тебя есть RawMaterialMovement в apps.sclad.models
        from apps.sclad.models import RawMaterialMovement as MovementModel
    except Exception:
        MovementModel = None

    # Если нет модели движений — всё, выходим
    if not MovementModel:
        return

    for it in recipe.items.all():
        need_qty = (produced * it.norm_per_kg).quantize(Decimal("0.000001"))

        # IMPORTANT: ниже поля могут отличаться у твоей модели движений.
        # Подгони названия полей под свою схему (я сделал наиболее типичный вариант).
        MovementModel.objects.create(
            material_name=it.material_name,
            movement_type="out",  # или "expense"/"writeoff" — смотри свои choices
            quantity=need_qty,
            reference_type="production_order",
            reference_id=order.id,
            note=f"Автосписание по рецептуре {recipe.product_name} v{recipe.version}",
        )
