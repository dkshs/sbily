from datetime import UTC
from datetime import datetime

from celery import shared_task

from sbily.users.models import User
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

    expired_links = ShortenedLink.objects.filter(
        remove_at__lte=datetime.now(tz=UTC),
    )
    expired_links_backup = list(expired_links)
    deleted_count = expired_links.delete()[0]
    if deleted_count > 0:
        users = [link.user for link in expired_links_backup]
        for user in set(users):
            links = [link for link in expired_links_backup if link.user == user]
            user.email_user(
                "Your links have expired",
                "emails/links_expired.html",
                links=links,
                links_count=len(links),
            )
    return get_task_response(
        "COMPLETED",
        f"Deleted {deleted_count} expired links.",
    )


@shared_task(
    bind=True,
    name="delete_excess_user_links",
    acks_late=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def delete_excess_user_links(self) -> dict[str, str | int]:
    """Delete excess links for users who have exceeded their link limits"""

    users = User.objects.filter(is_superuser=False)
    deleted_count = 0
    for user in users:
        links = user.shortened_links.order_by("-updated_at")
        link_num = user.link_num["links"] - user.max_num_links
        link_num_temp = user.link_num["temp_links"] - user.max_num_links_temporary
        if link_num > 0:
            links_to_delete = links.filter(remove_at__isnull=True)[:link_num]
            deleted_count += links.filter(pk__in=links_to_delete).delete()[0]
        if link_num_temp > 0:
            links_to_delete = links.filter(remove_at__isnull=False)[:link_num_temp]
            deleted_count += links.filter(pk__in=links_to_delete).delete()[0]

    return get_task_response(
        "COMPLETED",
        f"Deleted {deleted_count} excess links for users.",
    )
