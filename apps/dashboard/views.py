from datetime import date, timedelta

from django.db.models import Count, Sum
from django.views.generic import TemplateView

from apps.inventory.models import FlowerBatch
from apps.orders.models import Order


class DashboardView(TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sidebar_active"] = "dashboard"
        today = date.today()

        # KPI: orders today
        today_orders = Order.objects.filter(created_at__date=today)
        context["orders_today"] = today_orders.count()

        # KPI: revenue today
        revenue = today_orders.aggregate(total=Sum("total_price"))["total"] or 0
        context["revenue_today"] = f"₽{revenue:,.0f}".replace(",", " ")

        # KPI: average check
        if context["orders_today"] > 0:
            avg = revenue / context["orders_today"]
            context["avg_check"] = f"₽{avg:,.0f}".replace(",", " ")
        else:
            context["avg_check"] = "₽0"

        # KPI: expiring batches (within 2 days)
        expiry_threshold = today + timedelta(days=2)
        expiring = FlowerBatch.objects.filter(
            expiry_date__lte=expiry_threshold,
            status__in=["available", "low_stock"],
            quantity__gt=0,
        ).select_related("flower")

        context["hot_flowers_count"] = expiring.count()

        # Annotate expiring batches with days until expiry
        expiring_list = []
        for batch in expiring[:5]:
            batch.days_until_expiry = (batch.expiry_date - today).days
            expiring_list.append(batch)
        context["expiring_batches"] = expiring_list

        # Recent orders
        context["recent_orders"] = (
            Order.objects.select_related("customer")
            .prefetch_related("items__bouquet_recipe")
            .order_by("-created_at")[:6]
        )

        return context
