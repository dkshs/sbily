from datetime import UTC
from datetime import datetime

from celery import shared_task

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
    """
    Delete expired links from the database.

    Returns:
        Dict containing status and count of deleted links
    """
    try:
        self.update_state(state="PROGRESS")
        # Use select_for_update() to prevent race conditions
        expired_links = ShortenedLink.objects.select_for_update().filter(
            remove_at__lte=datetime.now(tz=UTC),
        )
        deleted_count = expired_links.delete()[0]
        self.update_state(state="COMPLETED")

    except Exception as e:
        self.update_state(state="FAILED")
        raise e
    else:
        return {"status": "COMPLETED", "deleted_count": deleted_count}
