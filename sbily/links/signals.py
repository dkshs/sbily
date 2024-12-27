import time

from django.db import IntegrityError
from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import DeletedShortenedLink
from .models import ShortenedLink
from .utils import filter_dict


@receiver(post_delete, sender=ShortenedLink)
def post_delete_shortened_link(sender, instance, **kwargs):
    """create a `DeleteShortenedLink` when a `ShortenedLink` is deleted"""
    retries = 3
    delay = 2  # seconds
    for attempt in range(retries):
        try:
            with transaction.atomic():
                data = filter_dict(instance.__dict__.copy(), {"_state", "id"})
                DeletedShortenedLink.objects.create(**data)
            break
        except IntegrityError as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                msg = f"Failed to create DeletedShortenedLink after {retries} attempts: {e}"  # noqa: E501
                raise RuntimeError(msg) from e
