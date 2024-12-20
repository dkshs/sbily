# ruff: noqa: BLE001
from typing import Any

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.shortcuts import get_object_or_404

from sbily.utils.tasks import get_task_response

from .models import User
from .utils.email import send_email_to_user


@shared_task(
    bind=True,
    name="send_welcome_email",
    max_retries=3,
    default_retry_delay=60,
)
def send_welcome_email(self, user_id: int) -> dict[str, Any]:
    """Send welcome email to newly registered user.

    Args:
        user_id: ID of user to send email to
    """

    try:
        user = get_object_or_404(User, id=user_id)
        name = user.get_short_name()

        subject = f"Welcome to Sbily, {name}!"
        template = "emails/welcome.html"

        send_email_to_user(user, subject, template)
        send_email_verification.apply_async([user.id], countdown=5)
    except Exception as exc:
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return get_task_response(
                "FAILED",
                f"Failed to send welcome email to user {user_id} after max retries.",
                str(exc),
                user_id=user_id,
            )
        return get_task_response(
            "RETRY",
            f"Retrying welcome email for user {user_id}",
            str(exc),
            user_id=user_id,
        )
    return get_task_response(
        "COMPLETED",
        f"Welcome email sent to {user.username}.",
        user_id=user_id,
    )


@shared_task(
    bind=True,
    name="send_email_verification",
    max_retries=3,
    default_retry_delay=60,
)
def send_email_verification(self, user_id: int) -> dict[str, Any]:
    """Send email verification link to user.

    Args:
        user_id: ID of user to send verification email to
    """
    try:
        user = get_object_or_404(User, id=user_id)

        subject = "Verify your email address"
        template = "emails/verify-email.html"
        verify_email_link = user.get_verify_email_link()
        send_email_to_user(
            user,
            subject,
            template,
            verify_email_link=verify_email_link,
        )
    except Exception as exc:
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return get_task_response(
                "FAILED",
                f"Failed to send verification email to user {user_id} after max retries.",
                str(exc),
                user_id=user_id,
            )
        return get_task_response(
            "RETRY",
            f"Retrying verification email for user {user_id}",
            str(exc),
            user_id=user_id,
        )
    return get_task_response(
        "COMPLETED",
        f"Verification email sent to {user.username}.",
        user_id=user_id,
    )
