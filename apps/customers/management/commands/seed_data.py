"""Management command to seed the database with test data."""

import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from faker import Faker

fake = Faker("ru_RU")


class Command(BaseCommand):
    help = "Заполнение базы данных тестовыми данными"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear-only",
            action="store_true",
            help="Только очистить данные без заполнения",
        )

    def handle(self, *args, **options):
        self._clear_data()
        self.stdout.write(self.style.SUCCESS("Данные очищены"))

        if options["clear_only"]:
            return

        users = self._create_users()
        flowers = self._create_flowers()
        suppliers = self._create_suppliers()
        batches = self._create_batches(flowers, suppliers)
        recipes = self._create_recipes(flowers)
        zones = self._create_delivery_zones()
        customers = self._create_customers()
        orders = self._create_orders(customers, recipes, zones, users)

        self.stdout.write(self.style.SUCCESS("\n=== Итого создано ==="))
        self.stdout.write(f"  Пользователи: {len(users)}")
        self.stdout.write(f"  Цветы: {len(flowers)}")
        self.stdout.write(f"  Поставщики: {len(suppliers)}")
        self.stdout.write(f"  Партии цветов: {len(batches)}")
        self.stdout.write(f"  Техкарты букетов: {len(recipes)}")
        self.stdout.write(f"  Зоны доставки: {len(zones)}")
        self.stdout.write(f"  Клиенты: {len(customers)}")
        self.stdout.write(f"  Заказы: {len(orders)}")

    def _clear_data(self):
        from apps.delivery.models import CourierShift, DeliveryZone
        from apps.inventory.models import (
            BouquetComponent,
            BouquetRecipe,
            Flower,
            FlowerBatch,
            Supplier,
            WriteOff,
        )
        from apps.orders.models import Order, OrderItem, OrderStatusLog

        # Delete in correct FK order
        OrderStatusLog.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        WriteOff.objects.all().delete()
        BouquetComponent.objects.all().delete()
        BouquetRecipe.objects.all().delete()
        FlowerBatch.objects.all().delete()
        CourierShift.objects.all().delete()
        DeliveryZone.objects.all().delete()

        from apps.customers.models import Customer

        Customer.objects.all().delete()

        Supplier.objects.all().delete()
        Flower.objects.all().delete()

        from apps.staff.models import User

        User.objects.filter(is_superuser=False).delete()

    def _create_users(self):
        from apps.staff.models import User, UserRole

        users = []
        user_data = [
            {
                "username": "admin",
                "password": "admin123",
                "role": UserRole.ADMIN,
                "first_name": "Арарат",
                "last_name": "Гулян",
                "is_staff": True,
            },
            {
                "username": "florist",
                "password": "florist123",
                "role": UserRole.FLORIST,
                "first_name": "Мария",
                "last_name": "Иванова",
                "is_staff": True,
            },
            {
                "username": "courier",
                "password": "courier123",
                "role": UserRole.COURIER,
                "first_name": "Дмитрий",
                "last_name": "Петров",
                "is_staff": False,
            },
        ]
        for data in user_data:
            password = data.pop("password")
            user = User.objects.create_user(**data)
            user.set_password(password)
            user.save()
            users.append(user)
            self.stdout.write(
                f"  Пользователь: {user.username} ({user.get_role_display()})"
            )

        return users

    def _create_flowers(self):
        from apps.inventory.models import Flower

        flowers_data = [
            {"name": "Роза красная", "category": "розы", "default_unit": "stem"},
            {
                "name": "Хризантема белая",
                "category": "хризантемы",
                "default_unit": "stem",
            },
            {"name": "Лилия", "category": "лилии", "default_unit": "stem"},
            {"name": "Тюльпан", "category": "тюльпаны", "default_unit": "stem"},
            {"name": "Гербера", "category": "герберы", "default_unit": "stem"},
        ]
        flowers = []
        for data in flowers_data:
            flower = Flower.objects.create(**data)
            flowers.append(flower)
            self.stdout.write(f"  Цветок: {flower.name}")
        return flowers

    def _create_suppliers(self):
        from apps.inventory.models import Supplier

        suppliers_data = [
            {
                "name": 'ООО "ФлораОпт"',
                "contact_phone": "+7 (495) 123-45-67",
                "email": "info@floraopt.ru",
            },
            {
                "name": "ИП Цветков",
                "contact_phone": "+7 (916) 987-65-43",
                "email": "tsvetkov@mail.ru",
            },
        ]
        suppliers = []
        for data in suppliers_data:
            supplier = Supplier.objects.create(**data)
            suppliers.append(supplier)
            self.stdout.write(f"  Поставщик: {supplier.name}")
        return suppliers

    def _create_batches(self, flowers, suppliers):
        from apps.inventory.models import BatchStatus, FlowerBatch

        today = date.today()
        batches = []

        for i in range(15):
            flower = random.choice(flowers)
            supplier = random.choice(suppliers)
            arrival_date = today - timedelta(days=random.randint(1, 14))
            # Some batches expiring soon (for "hot flowers" testing)
            if i < 4:
                expiry_date = today + timedelta(days=random.randint(0, 2))
            else:
                expiry_date = today + timedelta(days=random.randint(3, 10))

            batch = FlowerBatch.objects.create(
                flower=flower,
                supplier=supplier,
                arrival_date=arrival_date,
                expiry_date=expiry_date,
                quantity=random.randint(20, 100),
                unit_price=Decimal(str(random.randint(30, 150))),
                status=BatchStatus.AVAILABLE,
            )
            batches.append(batch)

        self.stdout.write(f"  Партии цветов: {len(batches)} шт.")
        return batches

    def _create_recipes(self, flowers):
        from apps.inventory.models import BouquetComponent, BouquetRecipe

        rose = flowers[0]
        chrysanthemum = flowers[1]
        lily = flowers[2]
        tulip = flowers[3]
        gerbera = flowers[4]

        recipes_data = [
            {
                "name": "Романтика",
                "description": "Классический букет из 11 красных роз",
                "packaging": "Крафт-бумага",
                "labor_cost": Decimal("300"),
                "margin_percent": Decimal("40"),
                "components": [(rose, 11)],
            },
            {
                "name": "Весенний",
                "description": "Весенний микс из тюльпанов и хризантем",
                "packaging": "Фетр",
                "labor_cost": Decimal("250"),
                "margin_percent": Decimal("35"),
                "components": [(tulip, 5), (chrysanthemum, 3)],
            },
            {
                "name": "Нежность",
                "description": "Нежный букет из лилий и гербер",
                "packaging": "Атласная лента",
                "labor_cost": Decimal("350"),
                "margin_percent": Decimal("30"),
                "components": [(lily, 7), (gerbera, 3)],
            },
            {
                "name": "Классика",
                "description": "Классический микс: розы, хризантемы, лилии",
                "packaging": "Коробка",
                "labor_cost": Decimal("400"),
                "margin_percent": Decimal("45"),
                "components": [(rose, 5), (chrysanthemum, 3), (lily, 3)],
            },
            {
                "name": "Мини",
                "description": "Компактный букет из гербер и тюльпанов",
                "packaging": "Плёнка",
                "labor_cost": Decimal("150"),
                "margin_percent": Decimal("50"),
                "components": [(gerbera, 3), (tulip, 2)],
            },
        ]

        recipes = []
        for data in recipes_data:
            components = data.pop("components")
            recipe = BouquetRecipe.objects.create(**data)
            for flower, qty in components:
                BouquetComponent.objects.create(
                    recipe=recipe, flower=flower, quantity=qty
                )
            recipes.append(recipe)
            self.stdout.write(f"  Техкарта: {recipe.name}")
        return recipes

    def _create_delivery_zones(self):
        from apps.delivery.models import DeliveryZone

        zones_data = [
            {
                "name": "Центр",
                "description": "Центральный район города",
                "base_price": Decimal("500"),
                "estimated_minutes": 30,
            },
            {
                "name": "Спальные районы",
                "description": "Спальные районы города",
                "base_price": Decimal("800"),
                "estimated_minutes": 45,
            },
            {
                "name": "Пригород",
                "description": "Пригородные зоны",
                "base_price": Decimal("1200"),
                "estimated_minutes": 60,
            },
        ]
        zones = []
        for data in zones_data:
            zone = DeliveryZone.objects.create(**data)
            zones.append(zone)
            self.stdout.write(f"  Зона доставки: {zone.name} ({zone.base_price} руб.)")
        return zones

    def _create_customers(self):
        from apps.customers.models import Customer, CustomerSegment

        segments = [s.value for s in CustomerSegment]
        today = date.today()
        customers = []

        for i in range(10):
            segment = random.choice(segments)
            memorable_dates = []
            if i < 4:
                # Some customers with memorable dates
                md_date = date(today.year, today.month, today.day) + timedelta(
                    days=random.randint(1, 30)
                )
                memorable_dates = [
                    {
                        "date": md_date.isoformat(),
                        "description": random.choice(
                            [
                                "День рождения",
                                "Годовщина свадьбы",
                                "День рождения мамы",
                                "День рождения жены",
                            ]
                        ),
                        "reminder_days_before": 3,
                    }
                ]

            customer = Customer.objects.create(
                phone=fake.phone_number(),
                email=fake.email() if random.random() > 0.3 else "",
                full_name=fake.name(),
                segment=segment,
                bonus_balance=(
                    Decimal(str(random.choice([0, 0, 100, 250, 500])))
                    if segment in ("regular", "vip")
                    else Decimal("0")
                ),
                memorable_dates=memorable_dates,
                all_channels=(
                    {"telegram": fake.user_name()} if random.random() > 0.5 else {}
                ),
                preferences=(
                    {"fav_flowers": random.choice(["розы", "лилии", "тюльпаны"])}
                    if random.random() > 0.5
                    else {}
                ),
            )
            customers.append(customer)

        self.stdout.write(f"  Клиенты: {len(customers)} шт.")
        return customers

    def _create_orders(self, customers, recipes, zones, users):
        from apps.orders.models import (
            Order,
            OrderItem,
            OrderSource,
            OrderStatus,
            OrderStatusLog,
            PaymentStatus,
            TimeSlot,
        )

        statuses = [s.value for s in OrderStatus]
        sources = [s.value for s in OrderSource]
        time_slots = [s.value for s in TimeSlot]
        today = date.today()

        florist = users[1]  # florist user
        courier = users[2]  # courier user

        orders = []
        for i in range(20):
            customer = random.choice(customers)
            recipe = random.choice(recipes)
            zone = random.choice(zones)
            status = random.choice(statuses)

            delivery_date = today + timedelta(days=random.randint(0, 7))
            quantity = random.randint(1, 3)
            unit_price = Decimal(str(random.randint(1500, 5000)))
            total_price = unit_price * quantity + zone.base_price

            payment_status = PaymentStatus.PENDING
            if status in (
                "paid",
                "assembling",
                "assembled",
                "delivering",
                "delivered",
                "completed",
            ):
                payment_status = PaymentStatus.PAID
            elif status == "refunded":
                payment_status = PaymentStatus.REFUNDED

            order = Order.objects.create(
                customer=customer,
                status=status,
                delivery_date=delivery_date,
                delivery_time_slot=random.choice(time_slots),
                delivery_address=fake.address(),
                delivery_zone=zone,
                total_price=total_price,
                payment_status=payment_status,
                assigned_florist=(
                    florist if status not in ("new", "cancelled") else None
                ),
                assigned_courier=(
                    courier
                    if status in ("delivering", "delivered", "completed")
                    else None
                ),
                source=random.choice(sources),
                notes=fake.sentence() if random.random() > 0.5 else "",
            )

            OrderItem.objects.create(
                order=order,
                bouquet_recipe=recipe,
                quantity=quantity,
                unit_price=unit_price,
            )

            # Create status log
            if status != "new":
                OrderStatusLog.objects.create(
                    order=order,
                    old_status="new",
                    new_status=status,
                    changed_by=users[0],
                    comment="Автоматически создано seed_data",
                )

            orders.append(order)

        self.stdout.write(f"  Заказы: {len(orders)} шт.")
        return orders
