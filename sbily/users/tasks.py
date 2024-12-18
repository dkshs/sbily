from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from .models import User


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
    except Exception:  # noqa: BLE001
        return False
    else:
        return True


@shared_task(bind=True, name="send_welcome_email", max_retries=3)
def send_welcome_email(self, user_id: int):
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
        send_email_verification.delay_on_commit(user.id)

    except Exception as exc:  # noqa: BLE001
        self.retry(exc=exc, countdown=60)  # Retry after 1 minute
        return {
            "status": "FAILED",
            "message": f"Failed to send welcome email to user {user_id}.",
            "error": str(exc),
        }
    else:
        return {
            "status": "COMPLETED",
            "message": f"Welcome email sent to {user.username}.",
            "user_id": user_id,
        }


@shared_task(bind=True, name="send_email_verification", max_retries=3)
def send_email_verification(self, user_id: int):
    """Send email verification link to user.

    Args:
        user_id: ID of user to send verification email to
    """
    try:
        user = get_object_or_404(User, id=user_id)

        subject = "Verify your email address"
        template = "emails/verify-email.html"
        send_email_to_user(
            user,
            subject,
            template,
            verify_email_link=user.get_verify_email_link(),
        )

    except Exception as exc:  # noqa: BLE001
        self.retry(exc=exc, countdown=60)  # Retry after 1 minute
        return {
            "status": "FAILED",
            "message": f"Failed to send verification email to user {user_id}.",
            "error": str(exc),
        }
    else:
        return {
            "status": "COMPLETED",
            "message": f"Verification email sent to {user.username}.",
            "user_id": user_id,
        }
