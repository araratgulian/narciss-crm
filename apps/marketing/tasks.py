import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def check_memorable_dates() -> int:
    """Daily task: find customers with upcoming memorable dates and send reminders."""
    from datetime import date, timedelta

    from apps.customers.models import Customer

    today = date.today()
    customers = Customer.objects.exclude(memorable_dates=[])
    reminders_sent = 0

    for customer in customers:
        for md in customer.memorable_dates:
            try:
                md_date = date.fromisoformat(md.get("date", ""))
                # Compare month and day (ignore year for recurring dates)
                reminder_days = md.get("reminder_days_before", 3)
                target = today + timedelta(days=reminder_days)
                if md_date.month == target.month and md_date.day == target.day:
                    logger.info(
                        "REMINDER: Customer %s (%s) has '%s' on %s",
                        customer.full_name,
                        customer.phone,
                        md.get("description", ""),
                        md["date"],
                    )
                    reminders_sent += 1
            except (ValueError, TypeError):
                continue

    logger.info("Memorable dates check: %d reminders", reminders_sent)
    return reminders_sent
