import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def check_expiring_batches() -> int:
    """Daily task: find FlowerBatch with expiry_date <= today + 2 days and status=AVAILABLE."""
    from datetime import date, timedelta

    from apps.inventory.models import BatchStatus, FlowerBatch

    threshold = date.today() + timedelta(days=2)
    expiring = FlowerBatch.objects.filter(
        status=BatchStatus.AVAILABLE,
        expiry_date__lte=threshold,
    )
    count = expiring.count()
    if count > 0:
        for batch in expiring:
            logger.warning(
                "HOT FLOWERS: %s (batch %d) expires on %s — %d units remaining",
                batch.flower.name,
                batch.pk,
                batch.expiry_date,
                batch.quantity,
            )
    logger.info("Expiring batches check: %d batches expiring within 2 days", count)
    return count
