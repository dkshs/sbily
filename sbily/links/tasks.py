from datetime import UTC
from datetime import datetime

from celery import shared_task

from .models import ShortenedLink


@shared_task(bind=True, name="delete_expired_links", acks_late=True)
def delete_expired_links(self):
    """Delete expired links from the database."""

    self.update_state(state="PROGRESS")
    expired_links = ShortenedLink.objects.filter(remove_at__lte=datetime.now(tz=UTC))
    deleted_count = expired_links.delete()[0]
    self.update_state(state="COMPLETED")

    return {"status": "COMPLETED", "deleted_count": deleted_count}
