from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import CustomerOrder


@receiver(pre_save, sender=CustomerOrder)
def remember_old_status(sender, instance: CustomerOrder, **kwargs):
    if not instance.pk:
        instance._old_status = None
        return
    old = CustomerOrder.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
    instance._old_status = old


@receiver(post_save, sender=CustomerOrder)
def notify_status_changed(sender, instance: CustomerOrder, created: bool, **kwargs):
    old_status = getattr(instance, "_old_status", None)
    if created:
        # можно тоже отправлять событие "создан заказ"
        return

    if old_status == instance.status:
        return  # статус не менялся

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "sales",  # группа (можно сделать по ролям/пользователям)
        {
            "type": "event",
            "data": {
                "type": "order_status_changed",
                "order_id": instance.id,
                "order_number": instance.order_number,
                "old_status": old_status,
                "new_status": instance.status,
                "new_status_label": instance.get_status_display(),
            },
        },
    )
