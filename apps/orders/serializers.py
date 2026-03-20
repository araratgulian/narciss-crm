from rest_framework import serializers

from .models import Order, OrderItem, OrderStatusLog


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("id", "bouquet_recipe", "quantity", "unit_price")


class OrderStatusLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusLog
        fields = ("id", "old_status", "new_status", "changed_by", "changed_at", "comment")
        read_only_fields = ("changed_at",)


class OrderListSerializer(serializers.ModelSerializer):
    """Light serializer for order list views."""

    customer_name = serializers.CharField(source="customer.full_name", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "customer_name",
            "status",
            "delivery_date",
            "delivery_time_slot",
            "total_price",
            "payment_status",
            "source",
            "created_at",
        )


class OrderDetailSerializer(serializers.ModelSerializer):
    """Full serializer for order detail views."""

    items = OrderItemSerializer(many=True, read_only=True)
    status_logs = OrderStatusLogSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "status",
            "delivery_date",
            "delivery_time_slot",
            "delivery_address",
            "delivery_zone",
            "total_price",
            "payment_status",
            "assigned_florist",
            "assigned_courier",
            "photo_before_delivery",
            "notes",
            "source",
            "items",
            "status_logs",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
