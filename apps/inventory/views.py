from datetime import date, timedelta

from django.db.models import F, Sum
from django.views.generic import ListView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import BouquetRecipe, Flower, FlowerBatch, Supplier
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


# --- Template-based views ---


class FlowerBatchListView(ListView):
    """HTML view listing flower batches (inventory)."""

    model = FlowerBatch
    template_name = "inventory/inventory_list.html"
    context_object_name = "batches"

    def get_queryset(self):
        return FlowerBatch.objects.select_related("flower", "supplier").order_by(
            "expiry_date"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sidebar_active"] = "inventory"

        batches = self.get_queryset()
        today = date.today()

        # Annotate batches with expiry info
        for batch in context["batches"]:
            batch.is_expiring = batch.expiry_date <= today + timedelta(days=2)

        # Summary stats
        active_batches = batches.filter(
            status__in=["available", "low_stock"], quantity__gt=0
        )
        context["total_items"] = active_batches.count()
        context["total_quantity"] = (
            active_batches.aggregate(total=Sum("quantity"))["total"] or 0
        )
        context["total_value"] = (
            active_batches.aggregate(
                total=Sum(F("quantity") * F("unit_price"))
            )["total"]
            or 0
        )

        # Expiring count
        context["expiring_count"] = active_batches.filter(
            expiry_date__lte=today + timedelta(days=2)
        ).count()

        # Flowers for filter dropdown
        context["flowers"] = Flower.objects.all()

        return context


class SupplierListView(ListView):
    """HTML view listing suppliers."""

    model = Supplier
    template_name = "inventory/supplier_list.html"
    context_object_name = "suppliers"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sidebar_active"] = "suppliers"
        return context
