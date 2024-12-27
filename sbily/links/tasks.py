from collections import defaultdict

from celery import shared_task
from django.utils import timezone

from sbily.users.models import User
from sbily.utils.tasks import get_task_response

from .models import DeletedShortenedLink
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
        remove_at__lte=timezone.now(),
    )
    deleted_count = 0

    user_links = defaultdict(list)
    for link in expired_links:
        user_links[link.user].append(link)
        link.delete()
        deleted_count += 1

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
        deleted_count=deleted_count,
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
    """Delete excess links for users that have exceeded their link limit."""
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


@shared_task(
    bind=True,
    name="cleanup_deleted_shortened_links",
    acks_late=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def cleanup_deleted_shortened_links(self) -> dict[str, str | int]:
    """Permanently deletes links that have been deleted."""
    links_to_delete = DeletedShortenedLink.objects.filter(
        user__is_superuser=False,
    )
    deleted_count = sum(
        link.delete()[0]
        for link in links_to_delete
        if link.time_until_permanent_deletion <= timezone.now()
    )
    return get_task_response(
        "COMPLETED",
        f"Permanently deleted {deleted_count} deleted links.",
        deleted_count=deleted_count,
    )
