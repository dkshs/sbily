import logging
from typing import Any

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from .models import User

logger = logging.getLogger(__name__)


def send_email_to_user(user: User, subject: str, template: str, **kwargs) -> bool:
    """Send an email to a user.

    Args:
        user: User object to send email to
        subject: Email subject line
        template: Email template to use
        **kwargs: Additional context data for the email template

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        context = {"user": user, "name": user.get_short_name()} | kwargs
        message = render_to_string(template, context)
        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=message,
        )
    except Exception as e:
        logger.exception(f"Failed to send email to {user.email}: {e!s}")
        return False
    else:
        return True


def get_task_response(
    status: str,
    message: str,
    user_id: int,
    error: str | None = None,
) -> dict[str, Any]:
    """Helper function to standardize task responses"""
    response = {
        "status": status,
        "message": message,
        "user_id": user_id,
    }
    if error:
        response["error"] = error
    return response


@shared_task(bind=True, name="send_welcome_email", max_retries=3)
def send_welcome_email(self, user_id: int) -> dict[str, Any]:
    """Send welcome email to newly registered user.

    Args:
        user_id: ID of user to send email to

    Returns:
        Dict containing task status and details
    """

    try:
        user = get_object_or_404(User, id=user_id)
        name = user.get_short_name()

        subject = f"Welcome to Sbily, {name}!"
        template = "emails/welcome.html"
        if not send_email_to_user(user, subject, template):
            raise Exception("Failed to send welcome email")

        send_email_verification.delay_on_commit(user.id)

    except Exception as exc:
        logger.exception(f"Error in welcome email task for user {user_id}: {exc!s}")
        self.retry(exc=exc, countdown=60)
        return get_task_response(
            "FAILED",
            f"Failed to send welcome email to user {user_id}.",
            user_id,
            str(exc),
        )

    return get_task_response(
        "COMPLETED",
        f"Welcome email sent to {user.username}.",
        user_id,
    )


@shared_task(bind=True, name="send_email_verification", max_retries=3)
def send_email_verification(self, user_id: int) -> dict[str, Any]:
    """Send email verification link to user.

    Args:
        user_id: ID of user to send verification email to

    Returns:
        Dict containing task status and details
    """
    try:
        user = get_object_or_404(User, id=user_id)

        subject = "Verify your email address"
        template = "emails/verify-email.html"
        if not send_email_to_user(
            user,
            subject,
            template,
            verify_email_link=user.get_verify_email_link(),
        ):
            raise Exception("Failed to send verification email")

    except Exception as exc:
        logger.exception(
            f"Error in verification email task for user {user_id}: {exc!s}"
        )
        self.retry(exc=exc, countdown=60)
        return get_task_response(
            "FAILED",
            f"Failed to send verification email to user {user_id}.",
            user_id,
            str(exc),
        )

    return get_task_response(
        "COMPLETED",
        f"Verification email sent to {user.username}.",
        user_id,
    )
