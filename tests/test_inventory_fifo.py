import datetime
from decimal import Decimal

import pytest

from apps.inventory.models import BatchStatus, FlowerBatch
from apps.inventory.services import (
    InsufficientStockError,
    assemble_bouquet,
    deduct_flowers_fifo,
)

from .factories import (
    BouquetComponentFactory,
    BouquetRecipeFactory,
    FlowerBatchFactory,
    FlowerFactory,
    SupplierFactory,
)


@pytest.mark.django_db
class TestDeductFlowersFifo:
    def test_deduct_fifo_single_batch_sufficient(self):
        """Deduction from a single batch with enough stock."""
        batch = FlowerBatchFactory(quantity=100)

        result = deduct_flowers_fifo(batch.flower_id, 30)

        assert len(result) == 1
        assert result[0]["batch_id"] == batch.pk
        assert result[0]["deducted_quantity"] == 30
        assert result[0]["remaining_quantity"] == 70

        batch.refresh_from_db()
        assert batch.quantity == 70

    def test_deduct_fifo_multiple_batches(self):
        """Deduction spans across multiple batches when first is insufficient."""
        flower = FlowerFactory()
        supplier = SupplierFactory()
        b1 = FlowerBatchFactory(
            flower=flower,
            supplier=supplier,
            quantity=30,
            arrival_date=datetime.date(2024, 1, 1),
        )
        b2 = FlowerBatchFactory(
            flower=flower,
            supplier=supplier,
            quantity=50,
            arrival_date=datetime.date(2024, 1, 2),
        )

        result = deduct_flowers_fifo(flower.pk, 60)

        assert len(result) == 2
        assert result[0]["batch_id"] == b1.pk
        assert result[0]["deducted_quantity"] == 30
        assert result[1]["batch_id"] == b2.pk
        assert result[1]["deducted_quantity"] == 30

    def test_deduct_fifo_insufficient_stock_raises_error(self):
        """Raises InsufficientStockError when total available < requested."""
        batch = FlowerBatchFactory(quantity=10)

        with pytest.raises(InsufficientStockError):
            deduct_flowers_fifo(batch.flower_id, 50)

        # Verify rollback — quantity unchanged
        batch.refresh_from_db()
        assert batch.quantity == 10

    def test_deduct_fifo_depletes_batch(self):
        """Batch status set to DEPLETED when quantity reaches 0."""
        batch = FlowerBatchFactory(quantity=20)

        deduct_flowers_fifo(batch.flower_id, 20)

        batch.refresh_from_db()
        assert batch.quantity == 0
        assert batch.status == BatchStatus.DEPLETED

    def test_deduct_fifo_oldest_first(self):
        """Oldest batch (by arrival_date) is deducted first."""
        flower = FlowerFactory()
        supplier = SupplierFactory()
        newer = FlowerBatchFactory(
            flower=flower,
            supplier=supplier,
            quantity=100,
            arrival_date=datetime.date(2024, 6, 1),
        )
        older = FlowerBatchFactory(
            flower=flower,
            supplier=supplier,
            quantity=100,
            arrival_date=datetime.date(2024, 1, 1),
        )

        result = deduct_flowers_fifo(flower.pk, 10)

        assert len(result) == 1
        assert result[0]["batch_id"] == older.pk

        older.refresh_from_db()
        newer.refresh_from_db()
        assert older.quantity == 90
        assert newer.quantity == 100


@pytest.mark.django_db
class TestAssembleBouquet:
    def test_assemble_bouquet_success(self):
        """Assembling a bouquet deducts all components from inventory."""
        flower1 = FlowerFactory()
        flower2 = FlowerFactory()
        supplier = SupplierFactory()
        FlowerBatchFactory(flower=flower1, supplier=supplier, quantity=100)
        FlowerBatchFactory(flower=flower2, supplier=supplier, quantity=100)

        recipe = BouquetRecipeFactory()
        BouquetComponentFactory(recipe=recipe, flower=flower1, quantity=5)
        BouquetComponentFactory(recipe=recipe, flower=flower2, quantity=3)

        cost = assemble_bouquet(recipe.pk)

        assert cost > Decimal("0")

        batch1 = FlowerBatch.objects.get(flower=flower1)
        batch2 = FlowerBatch.objects.get(flower=flower2)
        assert batch1.quantity == 95
        assert batch2.quantity == 97

    def test_assemble_bouquet_partial_failure_rollback(self):
        """If any component is insufficient, all deductions are rolled back."""
        flower1 = FlowerFactory()
        flower2 = FlowerFactory()
        supplier = SupplierFactory()
        FlowerBatchFactory(flower=flower1, supplier=supplier, quantity=100)
        FlowerBatchFactory(flower=flower2, supplier=supplier, quantity=2)

        recipe = BouquetRecipeFactory()
        BouquetComponentFactory(recipe=recipe, flower=flower1, quantity=5)
        BouquetComponentFactory(recipe=recipe, flower=flower2, quantity=10)

        with pytest.raises(InsufficientStockError):
            assemble_bouquet(recipe.pk)

        # Both batches should be unchanged due to rollback
        batch1 = FlowerBatch.objects.get(flower=flower1)
        batch2 = FlowerBatch.objects.get(flower=flower2)
        assert batch1.quantity == 100
        assert batch2.quantity == 2

    def test_assemble_bouquet_returns_cost(self):
        """Assemble bouquet returns correct total cost."""
        flower = FlowerFactory()
        supplier = SupplierFactory()
        FlowerBatchFactory(
            flower=flower, supplier=supplier, quantity=100, unit_price=Decimal("80.00")
        )

        recipe = BouquetRecipeFactory()
        BouquetComponentFactory(recipe=recipe, flower=flower, quantity=10)

        cost = assemble_bouquet(recipe.pk)

        assert cost == Decimal("800.00")  # 10 * 80.00
