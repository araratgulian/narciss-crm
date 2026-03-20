from rest_framework import serializers

from .models import Customer


class CustomerListSerializer(serializers.ModelSerializer):
    """Light serializer for customer list views."""

    class Meta:
        model = Customer
        fields = ("id", "phone", "full_name", "segment", "bonus_balance")


class CustomerDetailSerializer(serializers.ModelSerializer):
    """Full serializer for customer detail views."""

    class Meta:
        model = Customer
        fields = (
            "id",
            "phone",
            "email",
            "full_name",
            "all_channels",
            "preferences",
            "memorable_dates",
            "segment",
            "bonus_balance",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
