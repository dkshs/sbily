from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask

from .models import Token


@receiver(pre_delete, sender=Token)
def cancel_remove_token_task(sender: type, instance: Token, **kwargs) -> None:
    """
    Cancel the periodic task for removing a token when a Token is deleted.

    Args:
        sender: The model class that sent the signal
        instance: The actual instance being deleted
        **kwargs: Additional keyword arguments passed by the signal
    """
    PeriodicTask.objects.filter(name=f"Delete token {instance.id}").delete()
