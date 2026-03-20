from django.db import transaction

from apps.inventory.services import assemble_bouquet

from .models import Order, OrderStatusLog


class InvalidStatusTransitionError(Exception):
    """Raised when an order status transition is not allowed."""

    pass


VALID_TRANSITIONS: dict[str, list[str]] = {
    "new": ["paid", "cancelled"],
    "paid": ["assembling", "cancelled", "refunded"],
    "assembling": ["assembled", "cancelled"],
    "assembled": ["delivering", "cancelled"],
    "delivering": ["delivered"],
    "delivered": ["completed"],
    "completed": [],
    "cancelled": [],
    "refunded": [],
}


def transition_order_status(
    order_id: int, new_status: str, user, comment: str = ""
) -> Order:
    """
    Transition order to new status.

    Validates the transition, updates the order, creates a log entry,
    and triggers bouquet assembly when transitioning to 'assembling'.
    """
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order_id)
        old_status = order.status

        allowed = VALID_TRANSITIONS.get(old_status, [])
        if new_status not in allowed:
            raise InvalidStatusTransitionError(
                f"Cannot transition from '{old_status}' to '{new_status}'. "
                f"Allowed: {allowed}"
            )

        order.status = new_status
        order.save(update_fields=["status"])

        OrderStatusLog.objects.create(
            order=order,
            old_status=old_status,
            new_status=new_status,
            changed_by=user,
            comment=comment,
        )

        if new_status == "assembling":
            for item in order.items.select_related("bouquet_recipe"):
                for _ in range(item.quantity):
                    assemble_bouquet(
                        recipe_id=item.bouquet_recipe_id, order_id=order.pk
                    )

        return order
