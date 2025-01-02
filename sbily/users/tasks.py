# ruff: noqa: BLE001
from typing import Any
from urllib.parse import urljoin

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone

from sbily.utils.tasks import get_task_response

from .models import Token
from .models import User

BASE_URL = settings.BASE_URL or ""


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
        template = "emails/users/welcome.html"

        user.email_user(subject, template)
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
        template = "emails/users/verify-email.html"
        verify_email_link = user.get_verify_email_link()
        user.email_user(
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
                f"Failed to send verification email to user {user_id} after max retries.",  # noqa: E501
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


@shared_task(
    bind=True,
    name="send_password_changed_email",
    max_retries=3,
    default_retry_delay=60,
)
def send_password_changed_email(self, user_id: int) -> dict[str, Any]:
    """Send email informing user that their password has been changed.

    Args:
        user_id: ID of user to send email to
    """
    try:
        user = get_object_or_404(User, id=user_id)

        subject = "Your password has been changed!"
        template = "emails/users/password-changed.html"

        user.email_user(subject, template)
    except Exception as exc:
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return get_task_response(
                "FAILED",
                f"Failed to send password changed email to user {user_id} after max retries.",  # noqa: E501
                str(exc),
                user_id=user_id,
            )
        return get_task_response(
            "RETRY",
            f"Retrying password changed email for user {user_id}",
            str(exc),
            user_id=user_id,
        )
    return get_task_response(
        "COMPLETED",
        f"Password changed email sent to {user.username}.",
        user_id=user_id,
    )


@shared_task(
    bind=True,
    name="send_password_reset_email",
    max_retries=3,
    default_retry_delay=60,
)
def send_password_reset_email(self, user_id: int) -> dict[str, Any]:
    try:
        user = get_object_or_404(User, id=user_id)

        subject = "Reset your password"
        template = "emails/users/reset-password.html"
        reset_password_link = user.get_reset_password_link()
        user.email_user(
            subject,
            template,
            reset_password_link=reset_password_link,
        )
    except Exception as exc:
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return get_task_response(
                "FAILED",
                f"Failed to send password reset to user {user_id} after max retries.",
                str(exc),
                user_id=user_id,
            )
        return get_task_response(
            "RETRY",
            f"Retrying password reset email for user {user_id}",
            str(exc),
            user_id=user_id,
        )
    return get_task_response(
        "COMPLETED",
        f"Password reset email sent to {user.username}.",
        user_id=user_id,
    )


@shared_task(
    bind=True,
    name="send_sign_in_with_email",
    max_retries=3,
    default_retry_delay=60,
)
def send_sign_in_with_email(self, user_id: int) -> dict[str, Any]:
    try:
        user = get_object_or_404(User, id=user_id)

        token = user.tokens.filter(
            type=Token.TYPE_SIGN_IN_WITH_EMAIL,
        ).first() or user.tokens.create(type=Token.TYPE_SIGN_IN_WITH_EMAIL)
        if token.is_expired():
            token.renew()

        sign_in_with_email_path = reverse(
            "sign_in_with_email",
            kwargs={"token": token.token},
        )
        sign_in_with_email_link = urljoin(BASE_URL, sign_in_with_email_path)

        subject = "Sign in to your account"
        template = "emails/users/sign-in-with-email.html"
        user.email_user(
            subject,
            template,
            sign_in_with_email_link=sign_in_with_email_link,
        )
    except Exception as exc:
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return get_task_response(
                "FAILED",
                f"Failed to send sign in with email to user {user_id} after max retries.",  # noqa: E501
                str(exc),
                user_id=user_id,
            )
        return get_task_response(
            "RETRY",
            f"Retrying sign in with email for user {user_id}",
            str(exc),
            user_id=user_id,
        )
    return get_task_response(
        "COMPLETED",
        f"Sign in with email sent to {user.username}.",
        user_id=user_id,
    )


@shared_task(
    bind=True,
    name="cleanup_expired_tokens",
    acks_late=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def cleanup_expired_tokens(self) -> dict[str, str | int]:
    """Delete expired tokens from database."""
    tokens = Token.objects.filter(expires_at__lt=timezone.now())
    num_deleted = tokens.delete()[0]
    return get_task_response(
        "COMPLETED",
        f"Deleted {num_deleted} expired tokens.",
        num_deleted=num_deleted,
    )
