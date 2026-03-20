"""API URL configuration using DRF routers."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.customers.views import CustomerViewSet
from apps.delivery.views import DeliveryZoneViewSet
from apps.inventory.views import BouquetRecipeViewSet, FlowerBatchViewSet
from apps.orders.views import OrderViewSet

router = DefaultRouter()
router.register(r"customers", CustomerViewSet)
router.register(r"orders", OrderViewSet)
router.register(r"flower-batches", FlowerBatchViewSet)
router.register(r"bouquet-recipes", BouquetRecipeViewSet)
router.register(r"delivery-zones", DeliveryZoneViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
