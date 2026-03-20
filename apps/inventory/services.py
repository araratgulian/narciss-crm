from decimal import Decimal

from django.db import transaction

from .models import BatchStatus, BouquetRecipe, FlowerBatch


class InsufficientStockError(Exception):
    """Raised when not enough flowers in stock for deduction."""

    pass


def deduct_flowers_fifo(
    flower_id: int, quantity: int, order_id: int | None = None
) -> list[dict]:
    """
    Deduct flowers using FIFO (oldest batches first).

    Returns list of dicts: [{batch_id, deducted_quantity, remaining_quantity}]
    """
    with transaction.atomic():
        batches = (
            FlowerBatch.objects.select_for_update()
            .filter(flower_id=flower_id, status=BatchStatus.AVAILABLE)
            .order_by("arrival_date", "pk")
        )

        remaining = quantity
        deductions: list[dict] = []

        for batch in batches:
            if remaining <= 0:
                break

            deducted = min(batch.quantity, remaining)
            batch.quantity -= deducted
            remaining -= deducted

            if batch.quantity == 0:
                batch.status = BatchStatus.DEPLETED

            batch.save(update_fields=["quantity", "status"])

            deductions.append(
                {
                    "batch_id": batch.pk,
                    "deducted_quantity": deducted,
                    "remaining_quantity": batch.quantity,
                }
            )

        if remaining > 0:
            raise InsufficientStockError(
                f"Not enough stock for flower_id={flower_id}: "
                f"requested {quantity}, available {quantity - remaining}"
            )

        return deductions


def assemble_bouquet(recipe_id: int, order_id: int | None = None) -> Decimal:
    """
    Assemble a bouquet by deducting all components from inventory.

    Returns the total cost (sum of unit_price * deducted_qty for each batch used).
    """
    with transaction.atomic():
        recipe = BouquetRecipe.objects.prefetch_related(
            "recipe_components__flower"
        ).get(pk=recipe_id)

        total_cost = Decimal("0.00")

        for component in recipe.recipe_components.all():
            deductions = deduct_flowers_fifo(
                flower_id=component.flower_id,
                quantity=component.quantity,
                order_id=order_id,
            )

            for d in deductions:
                batch = FlowerBatch.objects.get(pk=d["batch_id"])
                total_cost += batch.unit_price * d["deducted_quantity"]

        return total_cost
