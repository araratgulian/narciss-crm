"""Celery configuration for Narciss CRM project."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("narciss_crm")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
