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
    expired_links = ShortenedLink.objects.select_related("user").filter(
        remove_at__lte=datetime.now(tz=UTC),
    )
    expired_links_backup = list(expired_links)
    deleted_count = expired_links.delete()[0]

    if deleted_count > 0:
        user_links = {}
        for link in expired_links_backup:
            if link.user not in user_links:
                user_links[link.user] = []
            user_links[link.user].append(link)

        for user, links in user_links.items():
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
    users = User.objects.filter(is_superuser=False).select_related()
    total_deleted_count = 0

    for user in users:
        links = user.shortened_links.order_by("-updated_at")
        link_num = user.link_num["links"] - user.max_num_links
        link_num_temp = user.link_num["temp_links"] - user.max_num_links_temporary
        user_deleted_count = 0

        if link_num > 0:
            links_to_delete = links.filter(remove_at__isnull=True)[:link_num]
            deleted = links.filter(pk__in=links_to_delete).delete()[0]
            user_deleted_count += deleted
            total_deleted_count += deleted
        if link_num_temp > 0:
            links_to_delete = links.filter(remove_at__isnull=False)[:link_num_temp]
            deleted = links.filter(pk__in=links_to_delete).delete()[0]
            user_deleted_count += deleted
            total_deleted_count += deleted
        if user_deleted_count > 0:
            user.email_user(
                "Your links have been deleted",
                "emails/links_deleted.html",
                links_count=user_deleted_count,
            )

    return get_task_response(
        "COMPLETED",
        f"Deleted {total_deleted_count} excess links for users.",
    )
