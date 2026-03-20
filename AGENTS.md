# AGENTS.md — Narciss CRM

> Контекст проекта для AI-агентов (Codex, Claude Code, Cursor, Perplexity Computer)

## Обзор проекта

**Narciss CRM** — специализированная CRM-система для сети цветочных магазинов «Нарцисс».
Два филиала: narciss.am (Ереван, Армения) и narciss24.ru (Ржев, Россия).
Пиковая нагрузка: 250 заказов/день (праздники — 8 Марта, 14 февраля, 1 сентября).

**Владелец**: Gulian Digital LLC (Ереван, Армения). CEO — Арарат Гулян.
**Предшественник**: amoCRM (Kommo), внедрённая для 9 магазинов в Ржеве.

## Технический стек

| Компонент | Технология | Версия |
|---|---|---|
| Backend | Django + Django REST Framework | 5.x |
| Frontend | HTMX + Tailwind CSS + Alpine.js | — |
| Database | PostgreSQL | 16 |
| Cache/Queue | Redis + Celery | — |
| Real-time | Django Channels + WebSocket | — |
| Mobile | PWA (Progressive Web App) | — |
| CI/CD | GitHub Actions | — |
| Hosting | DigitalOcean App Platform | — |
| Monitoring | Sentry + Django Debug Toolbar | — |
| Code style | ruff + black | — |
| Tests | pytest + factory_boy | — |

## Архитектура

```
narciss-crm/
├── .cursor/rules/          # Cursor rules для AI-ассистента
│   ├── django.mdc          # Django conventions
│   ├── flower.mdc          # Бизнес-логика цветочного магазина
│   └── testing.mdc         # Правила тестирования
├── .github/workflows/      # CI/CD
│   └── ci.yml
├── AGENTS.md               # Этот файл
├── README.md
├── apps/
│   ├── customers/           # Клиентская база (CRM ядро)
│   ├── orders/              # Управление заказами
│   ├── inventory/           # Складской учёт (FIFO)
│   ├── delivery/            # Управление доставкой
│   ├── analytics/           # Финансы и аналитика
│   ├── marketing/           # Рассылки, бонусы, триггеры
│   └── staff/               # Управление персоналом
├── config/                  # Django settings, urls, wsgi, asgi
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── templates/               # HTML-шаблоны (Tailwind CSS)
├── static/                  # Статика
├── api/                     # Django REST Framework endpoints
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/                   # Pytest
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
└── manage.py
```

## Django-приложения (apps)

### customers — Клиентская база
Единая карточка клиента с историей заказов, предпочтениями, памятными датами.
- Модели: `Customer`, `CustomerNote`
- Поля Customer: phone (primary key для поиска), email, full_name, all_channels JSON (telegram, whatsapp, instagram), preferences JSON (allergies, fav_flowers, color_palette), memorable_dates JSON, segment choices, bonus_balance, order_history

### orders — Управление заказами
Полный цикл заказа от приёма до завершения.
- Модели: `Order`, `OrderItem`, `OrderStatusLog`
- Статусы: new → paid → assembling → assembled → delivering → delivered → completed
- Каждая смена статуса → Celery-задача для уведомлений (клиент + персонал)
- Поля Order: customer FK, delivery_date, delivery_time_slot, delivery_address, total_price, payment_status, assigned_florist FK, assigned_courier FK, photo_before_delivery, notes

### inventory — Складской учёт
FIFO (First In, First Out) для скоропортящихся товаров.
- Модели: `FlowerBatch`, `BouquetRecipe`, `BouquetComponent`, `WriteOff`
- FlowerBatch: flower FK, supplier FK, arrival_date, expiry_date, quantity, unit_price, status
- BouquetRecipe (техкарта): name, components M2M через BouquetComponent(flower, quantity, unit), packaging, labor_cost, margin_percent → auto-calc selling_price
- При сборке букета — автоматическое списание компонентов из самых старых партий (FIFO)
- Celery-задача: ежедневная проверка expiry < 2 дней → алерт «горящие цветы»

### delivery — Управление доставкой
Зоны доставки, маршрутизация, PWA для курьеров.
- Модели: `DeliveryZone`, `CourierShift`
- DeliveryZone: name, polygon (GIS), base_price, estimated_time
- Интеграция: Google Maps API для маршрутизации
- PWA для курьеров: список заказов, навигация, фото-подтверждение
- WebSocket-уведомления о смене статуса доставки

### analytics — Финансы и аналитика
Дашборд с ключевыми метриками.
- Средний чек, LTV, маржинальность по позициям
- P&L по точкам продаж
- Сквозная аналитика: источник трафика → заказ → повторная покупка

### marketing — Рассылки и бонусы
- Триггерные рассылки: напоминание о памятной дате за 3 дня
- Бонусная программа: начисление и списание кэшбэка
- Сегментация клиентов

### staff — Управление персоналом
- Роли: admin, manager, florist, courier
- Графики смен, KPI

## Ключевые бизнес-правила

1. **FIFO-списание**: при сборке букета всегда списывать цветы из самой старой партии (earliest arrival_date с quantity > 0)
2. **Техкарта = рецепт**: BouquetRecipe определяет состав, упаковку, себестоимость. selling_price = (сумма компонентов + labor_cost) × (1 + margin_percent/100)
3. **Статусы заказа**: строгая последовательность, каждый переход логируется в OrderStatusLog с timestamp и user
4. **Горящие цветы**: партии с expiry_date < today + 2 дня выделяются визуально, менеджер получает push
5. **Списания**: обязательна причина (wilted, damaged, defective) — для аналитики потерь
6. **Памятные даты клиента**: автоматический триггер рассылки за 3 дня до даты
7. **Мультиканальность**: заказы приходят из сайта, WhatsApp, Telegram, телефона — все в единой воронке

## Интеграции

| Сервис | Назначение | Приоритет |
|---|---|---|
| narciss.am / narciss24.ru | Синхронизация каталога и заказов | Высокий |
| WhatsApp Business API | Приём заказов, уведомления | Высокий |
| Telegram Bot API | Приём заказов, уведомления курьерам | Высокий |
| ЮKassa / Stripe | Приём платежей | Высокий |
| Google Maps API | Маршрутизация доставки | Средний |
| 1С / МойСклад | Бухгалтерский учёт | Средний |

## Команды для разработки

```bash
# Запуск dev-окружения
docker compose up -d

# Миграции
docker compose exec web python manage.py migrate

# Тесты
docker compose exec web pytest --cov=apps -v

# Линтинг
ruff check .
black --check .

# Создание суперпользователя
docker compose exec web python manage.py createsuperuser
```

## Соглашения по коду

- **Python**: PEP 8, type hints для всех функций
- **Django**: CBV для CRUD, FBV для сложной логики
- **Модели**: каждая модель в отдельном файле (models/order.py, models/customer.py)
- **API**: Django REST Framework, ViewSets + Routers
- **Фильтрация**: django-filter
- **N+1**: всегда select_related / prefetch_related
- **i18n**: все строки через django.utils.translation (gettext_lazy)
- **Тесты**: pytest-django, factory_boy для фикстур
- **Код-стиль**: ruff для линтинга, black для форматирования
