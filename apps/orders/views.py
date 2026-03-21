from django.db.models import F, Sum
from django.views.generic import DetailView, ListView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Order, OrderStatusLog
from .serializers import OrderDetailSerializer, OrderListSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Order CRUD operations."""

    queryset = Order.objects.select_related(
        "customer", "delivery_zone", "assigned_florist", "assigned_courier"
    ).prefetch_related("items", "status_logs")
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "payment_status", "source", "delivery_date"]
    search_fields = ["customer__full_name", "customer__phone", "delivery_address"]
    ordering_fields = ["created_at", "delivery_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderDetailSerializer


# --- Template-based views ---


class OrderListView(ListView):
    """HTML view listing orders."""

    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    paginate_by = 20

    def get_queryset(self):
        return (
            Order.objects.select_related("customer", "delivery_zone")
            .prefetch_related("items__bouquet_recipe")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sidebar_active"] = "orders"
        return context


class OrderDetailView(DetailView):
    """HTML view for a single order."""

    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.select_related(
            "customer", "delivery_zone", "assigned_florist", "assigned_courier"
        ).prefetch_related("items__bouquet_recipe")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sidebar_active"] = "orders"
        order = self.object

        # Calculate subtotal from items
        items = order.items.all()
        subtotal = sum(item.unit_price * item.quantity for item in items)
        context["subtotal"] = subtotal

        # Annotate items with line_total
        for item in items:
            item.line_total = item.unit_price * item.quantity

        # Status logs
        context["status_logs"] = OrderStatusLog.objects.filter(
            order=order
        ).select_related("changed_by").order_by("changed_at")

        return context
