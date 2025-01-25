from celery import shared_task

from sbily.utils.tasks import default_task_params
from sbily.utils.tasks import task_response


@shared_task(**default_task_params("cleanup_clocked_schedules", acks_late=True))
def cleanup_clocked_schedules(self):
    """
    Clean up expired clocked schedules that are not associated with any periodic tasks.
    Also removes disabled periodic tasks containing 'Remove link' in their name.
    """
    from django_celery_beat.models import ClockedSchedule
    from django_celery_beat.models import PeriodicTask

    periodic_deleted = PeriodicTask.objects.filter(
        enabled=False,
        name__contains="Remove link ",
    ).delete()[0]

    schedule_deleted = ClockedSchedule.objects.filter(
        periodictask__isnull=True,
    ).delete()[0]

    return task_response(
        "COMPLETED",
        f"Cleaned up {schedule_deleted} expired clocked schedules and {periodic_deleted} disabled periodic tasks",  # noqa: E501
    )
