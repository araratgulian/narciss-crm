import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_order_notification(order_id: int, event: str) -> dict:
    """Send notification about order event. Currently a stub for future WhatsApp/Telegram integration."""
    from apps.orders.models import Order

    order = Order.objects.select_related("customer").get(pk=order_id)
    logger.info(
        "NOTIFICATION [%s]: Order #%d for %s (%s) — status: %s",
        event,
        order.pk,
        order.customer.full_name,
        order.customer.phone,
        order.get_status_display(),
    )
    # TODO: Implement WhatsApp/Telegram notifications
    return {"order_id": order_id, "event": event, "status": order.status}
