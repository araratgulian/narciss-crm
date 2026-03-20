import datetime
from decimal import Decimal

import factory

from apps.customers.models import Customer
from apps.delivery.models import DeliveryZone
from apps.inventory.models import (
    BatchStatus,
    BouquetComponent,
    BouquetRecipe,
    Flower,
    FlowerBatch,
    Supplier,
)
from apps.orders.models import Order, OrderItem, OrderStatus, TimeSlot
from apps.staff.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    phone = factory.Sequence(lambda n: f"+7900{n:07d}")
    full_name = factory.Faker("name", locale="ru_RU")
    email = factory.Faker("email")


class FlowerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Flower

    name = factory.Sequence(lambda n: f"Flower {n}")
    category = "roses"


class SupplierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Supplier

    name = factory.Sequence(lambda n: f"Supplier {n}")
    contact_phone = "+79001234567"


class FlowerBatchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FlowerBatch

    flower = factory.SubFactory(FlowerFactory)
    supplier = factory.SubFactory(SupplierFactory)
    arrival_date = factory.LazyFunction(datetime.date.today)
    expiry_date = factory.LazyFunction(
        lambda: datetime.date.today() + datetime.timedelta(days=7)
    )
    quantity = 100
    unit_price = Decimal("50.00")
    status = BatchStatus.AVAILABLE


class BouquetRecipeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BouquetRecipe

    name = factory.Sequence(lambda n: f"Bouquet {n}")
    labor_cost = Decimal("200.00")
    margin_percent = Decimal("30.00")


class BouquetComponentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BouquetComponent

    recipe = factory.SubFactory(BouquetRecipeFactory)
    flower = factory.SubFactory(FlowerFactory)
    quantity = 5


class DeliveryZoneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DeliveryZone

    name = factory.Sequence(lambda n: f"Zone {n}")
    base_price = Decimal("500.00")
    estimated_minutes = 30


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    customer = factory.SubFactory(CustomerFactory)
    status = OrderStatus.NEW
    delivery_date = factory.LazyFunction(
        lambda: datetime.date.today() + datetime.timedelta(days=1)
    )
    delivery_time_slot = TimeSlot.SLOT_09_12
    delivery_address = "Test address"
    delivery_zone = factory.SubFactory(DeliveryZoneFactory)
    total_price = Decimal("5000.00")


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    bouquet_recipe = factory.SubFactory(BouquetRecipeFactory)
    quantity = 1
    unit_price = Decimal("5000.00")
