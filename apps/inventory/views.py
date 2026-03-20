from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import BouquetRecipe, FlowerBatch
from .serializers import (
    BouquetRecipeDetailSerializer,
    BouquetRecipeListSerializer,
    FlowerBatchDetailSerializer,
    FlowerBatchListSerializer,
)


class FlowerBatchViewSet(viewsets.ModelViewSet):
    """ViewSet for FlowerBatch CRUD operations."""

    queryset = FlowerBatch.objects.select_related("flower", "supplier")
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "flower", "supplier"]
    search_fields = ["flower__name", "supplier__name"]
    ordering_fields = ["arrival_date", "expiry_date", "quantity"]

    def get_serializer_class(self):
        if self.action == "list":
            return FlowerBatchListSerializer
        return FlowerBatchDetailSerializer


class BouquetRecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for BouquetRecipe CRUD operations."""

    queryset = BouquetRecipe.objects.prefetch_related("recipe_components__flower")
    permission_classes = [IsAuthenticated]
    filterset_fields = ["is_active"]
    search_fields = ["name"]
    ordering_fields = ["name"]

    def get_serializer_class(self):
        if self.action == "list":
            return BouquetRecipeListSerializer
        return BouquetRecipeDetailSerializer
