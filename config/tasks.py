from celery import shared_task
from django.utils.timezone import now
from django.utils.timezone import timedelta

from sbily.utils.tasks import default_task_params
from sbily.utils.tasks import task_response


@shared_task(**default_task_params("cleanup_clocked_schedules", acks_late=True))
def cleanup_clocked_schedules(self):
    """
    Clean up expired clocked schedules that are not associated with any periodic tasks.
    Also removes disabled periodic tasks containing 'Remove link' and
    'Remove deleted link' in their name.
    """
    from django_celery_beat.models import ClockedSchedule
    from django_celery_beat.models import PeriodicTask

    periodic_tasks = PeriodicTask.objects.filter(
        enabled=False,
        name__regex=r"^(Remove link|Remove deleted link)",
    )

    threshold_time = now() + timedelta(minutes=5)
    periodic_tasks.filter(clocked__clocked_time__gte=threshold_time).update(
        enabled=True,
    )

    periodic_deleted = periodic_tasks.delete()[0]
    schedule_deleted = ClockedSchedule.objects.filter(
        periodictask__isnull=True,
    ).delete()[0]

    return task_response(
        "COMPLETED",
        f"Cleaned up {schedule_deleted} expired clocked schedules and {periodic_deleted} disabled periodic tasks",  # noqa: E501
    )
