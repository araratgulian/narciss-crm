from decimal import Decimal

import pytest

from .factories import (
    BouquetComponentFactory,
    BouquetRecipeFactory,
    FlowerBatchFactory,
    FlowerFactory,
    SupplierFactory,
)


@pytest.mark.django_db
class TestBouquetPricing:
    def test_component_cost_calculation(self):
        """component_cost = sum of (avg unit_price * component quantity)."""
        flower = FlowerFactory()
        supplier = SupplierFactory()
        # Two batches with different prices: avg = (100 + 200) / 2 = 150
        FlowerBatchFactory(
            flower=flower, supplier=supplier, unit_price=Decimal("100.00")
        )
        FlowerBatchFactory(
            flower=flower, supplier=supplier, unit_price=Decimal("200.00")
        )

        recipe = BouquetRecipeFactory(labor_cost=Decimal("0.00"))
        BouquetComponentFactory(recipe=recipe, flower=flower, quantity=10)

        # avg_price = 150, quantity = 10 → cost = 1500
        assert recipe.component_cost == Decimal("1500.00")

    def test_selling_price_formula(self):
        """selling_price = (component_cost + labor_cost) * (1 + margin/100)."""
        flower = FlowerFactory()
        supplier = SupplierFactory()
        FlowerBatchFactory(
            flower=flower, supplier=supplier, unit_price=Decimal("100.00")
        )

        recipe = BouquetRecipeFactory(
            labor_cost=Decimal("200.00"), margin_percent=Decimal("50.00")
        )
        BouquetComponentFactory(recipe=recipe, flower=flower, quantity=10)

        # component_cost = 100 * 10 = 1000
        # selling_price = (1000 + 200) * 1.5 = 1800
        assert recipe.selling_price == Decimal("1800.00")

    def test_update_cached_price(self):
        """update_cached_price saves selling_price to cached_selling_price."""
        flower = FlowerFactory()
        supplier = SupplierFactory()
        FlowerBatchFactory(
            flower=flower, supplier=supplier, unit_price=Decimal("100.00")
        )

        recipe = BouquetRecipeFactory(
            labor_cost=Decimal("200.00"), margin_percent=Decimal("50.00")
        )
        BouquetComponentFactory(recipe=recipe, flower=flower, quantity=10)

        assert recipe.cached_selling_price is None

        recipe.update_cached_price()
        recipe.refresh_from_db()

        assert recipe.cached_selling_price == Decimal("1800.00")
