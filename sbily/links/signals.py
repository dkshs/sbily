from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask

from .models import ShortenedLink


@receiver(pre_delete, sender=ShortenedLink)
def cancel_remove_link_task(sender: type, instance: ShortenedLink, **kwargs) -> None:
    """
    Cancel the periodic task for removing a link when a ShortenedLink is deleted.

    Args:
        sender: The model class that sent the signal
        instance: The actual instance being deleted
        **kwargs: Additional keyword arguments passed by the signal
    """
    PeriodicTask.objects.filter(name=f"Remove link {instance.id}").delete()
