"""Celery configuration for Narciss CRM project."""

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("narciss_crm")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check-expiring-batches": {
        "task": "apps.inventory.tasks.check_expiring_batches",
        "schedule": crontab(hour=8, minute=0),
    },
    "check-memorable-dates": {
        "task": "apps.marketing.tasks.check_memorable_dates",
        "schedule": crontab(hour=9, minute=0),
    },
}
