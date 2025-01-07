from collections import defaultdict
from urllib.parse import urljoin

from celery import shared_task
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from sbily.users.models import User
from sbily.utils.tasks import default_task_params
from sbily.utils.tasks import task_response

from .models import DeletedShortenedLink
from .models import ShortenedLink

SITE_BASE_URL = settings.BASE_URL or ""


@shared_task(**default_task_params("delete_expired_links", acks_late=True))
def delete_expired_links(self):
    """Delete expired links from the database."""
    expired_links = ShortenedLink.objects.select_related("user").filter(
        remove_at__lte=timezone.now(),
    )
    expired_links_backup = list(expired_links)
    deleted_count = expired_links.delete()[0]
    deleted_links_url = urljoin(SITE_BASE_URL, reverse("deleted_links"))

    if deleted_count > 0:
        user_links = defaultdict(list)
        for link in expired_links_backup:
            user_links[link.user].append(link)

        for user, links in user_links.items():
            user.email_user(
                "Your links have expired",
                "emails/links/links_expired.html",
                links=links,
                links_count=len(links),
                deleted_links_url=deleted_links_url,
            )
    return task_response(
        "COMPLETED",
        f"Deleted {deleted_count} expired links.",
        deleted_count=deleted_count,
    )


@shared_task(**default_task_params("delete_excess_user_links", acks_late=True))
def delete_excess_user_links(self):
    """Delete excess links for users that have exceeded their link limit."""
    users = User.objects.prefetch_related("shortened_links").all()
    total_deleted_count = 0
    deleted_links_url = urljoin(SITE_BASE_URL, reverse("deleted_links"))

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
                "emails/links/links_deleted.html",
                links_count=user_deleted_count,
                deleted_links_url=deleted_links_url,
            )

    return task_response(
        "COMPLETED",
        f"Deleted {total_deleted_count} excess links for users.",
    )


@shared_task(**default_task_params("cleanup_deleted_shortened_links", acks_late=True))
def cleanup_deleted_shortened_links(self):
    """Permanently deletes links that have been deleted."""
    links_to_delete = DeletedShortenedLink.objects.all()
    deleted_count = sum(
        link.delete()[0]
        for link in links_to_delete
        if link.time_until_permanent_deletion <= timezone.now()
    )
    return task_response(
        "COMPLETED",
        f"Permanently deleted {deleted_count} deleted links.",
        deleted_count=deleted_count,
    )
