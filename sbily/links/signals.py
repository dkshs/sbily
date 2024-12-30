import time
from typing import Any

from django.db import IntegrityError
from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import DeletedShortenedLink
from .models import ShortenedLink
from .utils import filter_dict


@receiver(post_delete, sender=ShortenedLink)
def post_delete_shortened_link(sender: type, instance: ShortenedLink, **kwargs) -> None:
    """
    Create a DeletedShortenedLink record when a ShortenedLink is deleted.

    Args:
        sender: The model class that sent the signal
        instance: The actual instance being deleted
        **kwargs: Additional keyword arguments passed by the signal

    Raises:
        RuntimeError: If unable to create DeletedShortenedLink after retries
    """
    max_retries = 3
    delay_seconds = 2

    for attempt in range(max_retries):
        try:
            with transaction.atomic():
                data: dict[str, Any] = filter_dict(
                    instance.__dict__.copy(),
                    {"_state", "id"},
                )
                if instance.is_expired():
                    data["remove_at"] = timezone.now() + instance.DEFAULT_EXPIRY
                DeletedShortenedLink.objects.create(**data)
                break
        except IntegrityError as e:
            if attempt < max_retries - 1:
                time.sleep(delay_seconds)
            else:
                msg = (
                    f"Failed to create DeletedShortenedLink after "
                    f"{max_retries} attempts: {e}"
                )
                raise RuntimeError(msg) from e
