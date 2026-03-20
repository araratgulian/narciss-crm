# Narciss CRM

CRM-система для сети цветочных магазинов «Нарцисс».

## О проекте

**Narciss CRM** — специализированная CRM для управления заказами, складом, доставкой и клиентской базой цветочных магазинов. Два филиала: [narciss.am](https://narciss.am) (Ереван, Армения) и [narciss24.ru](https://narciss24.ru) (Ржев, Россия).

### Основные возможности

- **Клиентская база** — карточки клиентов с предпочтениями, памятными датами, бонусной программой
- **Управление заказами** — полный цикл от приёма до доставки с отслеживанием статусов
- **Складской учёт** — FIFO-списание для скоропортящихся товаров, техкарты букетов
- **Доставка** — зоны доставки, графики курьеров, временные слоты
- **Аналитика** — средний чек, LTV, маржинальность, P&L
- **Маркетинг** — триггерные рассылки, бонусная программа, сегментация

## Технический стек

| Компонент | Технология |
|---|---|
| Backend | Django 5.x + Django REST Framework |
| База данных | PostgreSQL 16 |
| Кэш / Очереди | Redis + Celery |
| CI/CD | GitHub Actions |
| Код-стиль | ruff + black |
| Тесты | pytest + factory_boy |

## Быстрый старт (Docker)

```bash
# Клонировать репозиторий
git clone https://github.com/araratgulian/narciss-crm.git
cd narciss-crm

# Скопировать файл окружения
cp .env.example .env

# Запустить через Docker Compose
docker compose -f docker/docker-compose.yml up -d

# Применить миграции
docker compose -f docker/docker-compose.yml exec web python manage.py migrate

# Создать суперпользователя
docker compose -f docker/docker-compose.yml exec web python manage.py createsuperuser
```

Приложение будет доступно по адресу: http://localhost:8000

## Разработка (локально)

```bash
# Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate

# Установить зависимости
pip install -r requirements/dev.txt

# Скопировать файл окружения
cp .env.example .env

# Применить миграции
python manage.py migrate

# Запустить сервер
python manage.py runserver
```

## Тесты и линтинг

```bash
# Запуск тестов
pytest --cov=apps -v

# Линтинг
ruff check .

# Проверка форматирования
black --check .
```

## Структура проекта

```
narciss-crm/
├── apps/
│   ├── customers/      # Клиентская база
│   ├── orders/         # Управление заказами
│   ├── inventory/      # Складской учёт (FIFO)
│   ├── delivery/       # Управление доставкой
│   ├── analytics/      # Аналитика (в разработке)
│   ├── marketing/      # Маркетинг (в разработке)
│   └── staff/          # Управление персоналом
├── api/                # DRF endpoints
├── config/             # Django настройки
│   └── settings/
│       ├── base.py
│       ├── dev.py
│       └── prod.py
├── docker/             # Docker конфигурация
├── requirements/       # Зависимости
├── templates/          # HTML шаблоны
├── static/             # Статические файлы
└── tests/              # Тесты
```

## Лицензия

Проприетарное ПО. © Gulian Digital LLC
