from datetime import UTC
from datetime import datetime

from celery import shared_task

from sbily.utils.tasks import get_task_response

from .models import ShortenedLink


@shared_task(
    bind=True,
    name="delete_expired_links",
    acks_late=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def delete_expired_links(self) -> dict[str, str | int]:
    """Delete expired links from the database"""

    expired_links = ShortenedLink.objects.select_for_update().filter(
        remove_at__lte=datetime.now(tz=UTC),
    )
    deleted_count = expired_links.delete()[0]
    return get_task_response(
        "COMPLETED",
        f"Deleted {deleted_count} expired links.",
    )
