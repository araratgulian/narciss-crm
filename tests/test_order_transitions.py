import pytest

from apps.orders.models import OrderStatus, OrderStatusLog
from apps.orders.services import InvalidStatusTransitionError, transition_order_status

from .factories import (
    BouquetComponentFactory,
    BouquetRecipeFactory,
    FlowerBatchFactory,
    FlowerFactory,
    OrderFactory,
    OrderItemFactory,
    SupplierFactory,
    UserFactory,
)


@pytest.mark.django_db
class TestOrderTransitions:
    def test_valid_transition_new_to_paid(self):
        """Order can transition from new to paid."""
        order = OrderFactory(status=OrderStatus.NEW)
        user = UserFactory()

        updated = transition_order_status(order.pk, "paid", user)

        assert updated.status == "paid"

    def test_invalid_transition_new_to_delivered(self):
        """Cannot skip statuses — new to delivered is invalid."""
        order = OrderFactory(status=OrderStatus.NEW)
        user = UserFactory()

        with pytest.raises(InvalidStatusTransitionError):
            transition_order_status(order.pk, "delivered", user)

        order.refresh_from_db()
        assert order.status == "new"

    def test_transition_creates_status_log(self):
        """Each transition creates an OrderStatusLog entry."""
        order = OrderFactory(status=OrderStatus.NEW)
        user = UserFactory()

        transition_order_status(order.pk, "paid", user, comment="Payment received")

        log = OrderStatusLog.objects.get(order=order)
        assert log.old_status == "new"
        assert log.new_status == "paid"
        assert log.changed_by == user
        assert log.comment == "Payment received"

    def test_transition_to_assembling_triggers_fifo(self):
        """Transitioning to 'assembling' triggers FIFO deduction for order items."""
        flower = FlowerFactory()
        supplier = SupplierFactory()
        FlowerBatchFactory(flower=flower, supplier=supplier, quantity=100)

        recipe = BouquetRecipeFactory()
        BouquetComponentFactory(recipe=recipe, flower=flower, quantity=5)

        order = OrderFactory(status=OrderStatus.PAID)
        OrderItemFactory(order=order, bouquet_recipe=recipe, quantity=2)

        user = UserFactory()
        transition_order_status(order.pk, "assembling", user)

        from apps.inventory.models import FlowerBatch

        batch = FlowerBatch.objects.get(flower=flower)
        # 2 bouquets * 5 flowers each = 10 deducted
        assert batch.quantity == 90

    def test_cancelled_from_any_valid_state(self):
        """Order can be cancelled from new, paid, assembling, assembled."""
        user = UserFactory()

        for status in ["new", "paid", "assembling", "assembled"]:
            order = OrderFactory(status=status)
            updated = transition_order_status(order.pk, "cancelled", user)
            assert updated.status == "cancelled"

    def test_completed_and_cancelled_are_terminal(self):
        """Completed and cancelled orders cannot transition further."""
        user = UserFactory()

        for terminal_status in ["completed", "cancelled", "refunded"]:
            order = OrderFactory(status=terminal_status)

            with pytest.raises(InvalidStatusTransitionError):
                transition_order_status(order.pk, "new", user)
