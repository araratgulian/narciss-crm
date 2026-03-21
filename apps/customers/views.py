from django.db.models import Avg, Count, Sum
from django.views.generic import DetailView, ListView
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


# --- Template-based views ---


class CustomerListView(ListView):
    """HTML view listing customers."""

    model = Customer
    template_name = "customers/customer_list.html"
    context_object_name = "customers"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sidebar_active"] = "customers"
        return context


class CustomerDetailView(DetailView):
    """HTML view for a single customer profile."""

    model = Customer
    template_name = "customers/customer_detail.html"
    context_object_name = "customer"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sidebar_active"] = "customers"
        customer = self.object

        # Orders for this customer
        orders = customer.orders.prefetch_related("items__bouquet_recipe").order_by(
            "-created_at"
        )
        context["orders"] = orders

        # Customer stats
        stats = orders.aggregate(
            total_orders=Count("pk"),
            ltv=Sum("total_price"),
            avg_check=Avg("total_price"),
        )
        stats["total_orders"] = stats["total_orders"] or 0
        stats["ltv"] = stats["ltv"] or 0
        stats["avg_check"] = stats["avg_check"] or 0

        last_order = orders.first()
        if last_order:
            stats["last_order_date"] = last_order.created_at.strftime("%d.%m.%Y")
        else:
            stats["last_order_date"] = None

        context["customer_stats"] = stats
        return context
