from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.FlowerBatchListView.as_view(), name="flower_list"),
    path("suppliers/", views.SupplierListView.as_view(), name="supplier_list"),
]
