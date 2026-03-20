from rest_framework import serializers

from .models import BouquetComponent, BouquetRecipe, FlowerBatch


class FlowerBatchListSerializer(serializers.ModelSerializer):
    """Light serializer for flower batch list views."""

    flower_name = serializers.CharField(source="flower.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = FlowerBatch
        fields = (
            "id",
            "flower",
            "flower_name",
            "supplier",
            "supplier_name",
            "arrival_date",
            "expiry_date",
            "quantity",
            "unit_price",
            "status",
        )


class FlowerBatchDetailSerializer(serializers.ModelSerializer):
    """Full serializer for flower batch detail views."""

    class Meta:
        model = FlowerBatch
        fields = (
            "id",
            "flower",
            "supplier",
            "arrival_date",
            "expiry_date",
            "quantity",
            "unit_price",
            "status",
            "created_at",
        )
        read_only_fields = ("created_at",)


class BouquetComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BouquetComponent
        fields = ("id", "flower", "quantity", "unit")


class BouquetRecipeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BouquetRecipe
        fields = ("id", "name", "margin_percent", "is_active")


class BouquetRecipeDetailSerializer(serializers.ModelSerializer):
    recipe_components = BouquetComponentSerializer(many=True, read_only=True)
    selling_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    component_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = BouquetRecipe
        fields = (
            "id",
            "name",
            "description",
            "packaging",
            "labor_cost",
            "margin_percent",
            "is_active",
            "image",
            "recipe_components",
            "component_cost",
            "selling_price",
            "cached_selling_price",
        )
