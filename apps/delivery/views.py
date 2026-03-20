from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import DeliveryZone
from .serializers import DeliveryZoneSerializer


class DeliveryZoneViewSet(viewsets.ModelViewSet):
    """ViewSet for DeliveryZone CRUD operations."""

    queryset = DeliveryZone.objects.all()
    serializer_class = DeliveryZoneSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["is_active"]
    search_fields = ["name"]
    ordering_fields = ["name", "base_price"]
