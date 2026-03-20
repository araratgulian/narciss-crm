from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Customer
from .serializers import CustomerDetailSerializer, CustomerListSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for Customer CRUD operations."""

    queryset = Customer.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ["segment"]
    search_fields = ["full_name", "phone", "email"]
    ordering_fields = ["created_at", "full_name"]

    def get_serializer_class(self):
        if self.action == "list":
            return CustomerListSerializer
        return CustomerDetailSerializer
