from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Order
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
