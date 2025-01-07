from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.utils import timezone

from sbily.utils.tasks import default_task_params
from sbily.utils.tasks import task_response

from .models import Token
from .models import User

BASE_URL = settings.BASE_URL or ""

logger = get_task_logger(__name__)


@shared_task(**default_task_params("send_welcome_email"))
def send_welcome_email(self, user_id: int):
    """Send welcome email to newly registered user."""
    user = User.objects.get(id=user_id)
    name = user.get_short_name()

    subject = f"Welcome to Sbily, {name}!"
    template = "emails/users/welcome.html"

    user.email_user(subject, template)
    try:
        send_email_verification.apply_async([user.id], countdown=5)
    except Exception:
        logger.exception("Failed to send verification email to %s", user.username)

    return task_response(
        "COMPLETED",
        f"Welcome email sent to {user.username}.",
        user_id=user_id,
    )


@shared_task(**default_task_params("send_email_verification"))
def send_email_verification(self, user_id: int):
    """Send email verification link to user."""
    user = User.objects.get(id=user_id)

    subject = "Verify your email address"
    template = "emails/users/verify-email.html"
    verify_email_link = user.get_verify_email_link()

    user.email_user(
        subject,
        template,
        verify_email_link=verify_email_link,
    )
    return task_response(
        "COMPLETED",
        f"Verification email sent to {user.username}.",
        user_id=user_id,
    )


@shared_task(**default_task_params("send_password_changed_email"))
def send_password_changed_email(self, user_id: int):
    """Send email informing user that their password has been changed."""
    user = User.objects.get(id=user_id)

    subject = "Your password has been changed!"
    template = "emails/users/password-changed.html"

    user.email_user(subject, template)
    return task_response(
        "COMPLETED",
        f"Password changed email sent to {user.username}.",
        user_id=user_id,
    )


@shared_task(**default_task_params("send_password_reset_email"))
def send_password_reset_email(self, user_id: int):
    """Send password reset link to user."""
    user = User.objects.get(id=user_id)

    subject = "Reset your password"
    template = "emails/users/reset-password.html"
    reset_password_link = user.get_reset_password_link()

    user.email_user(
        subject,
        template,
        reset_password_link=reset_password_link,
    )
    return task_response(
        "COMPLETED",
        f"Password reset email sent to {user.username}.",
        user_id=user_id,
    )


@shared_task(**default_task_params("send_sign_in_with_email"))
def send_sign_in_with_email(self, user_id: int):
    """Send sign in with email link to user."""
    user = User.objects.get(id=user_id)

    subject = "Sign in to your account"
    template = "emails/users/sign-in-with-email.html"
    sign_in_with_email_link = user.get_token_link(
        Token.TYPE_SIGN_IN_WITH_EMAIL,
        "sign_in_with_email_verify",
    )

    user.email_user(
        subject,
        template,
        sign_in_with_email_link=sign_in_with_email_link,
    )
    return task_response(
        "COMPLETED",
        f"Sign in with email sent to {user.username}.",
        user_id=user_id,
    )


@shared_task(**default_task_params("send_deactivated_account_email"))
def send_deactivated_account_email(self, user_id: int):
    """Send email informing user that their account has been deactivated."""
    user = User.objects.get(id=user_id)

    subject = "Your account has been deactivated"
    template = "emails/users/deactivated-account.html"
    account_activation_link = user.get_account_activation_link()

    user.email_user(
        subject,
        template,
        account_activation_link=account_activation_link,
    )
    user.shortened_links.update(is_active=False)
    user.deleted_shortened_links.update(is_active=False)
    return task_response(
        "COMPLETED",
        f"Deactivated account email sent to {user.username}.",
        user_id=user_id,
    )


@shared_task(**default_task_params("send_account_activation_email"))
def send_account_activation_email(self, user_id: int):
    """Send account activation email."""
    user = User.objects.get(id=user_id)

    subject = "Activate your account"
    template = "emails/users/activate-account.html"
    account_activation_link = user.get_account_activation_link()

    user.email_user(
        subject,
        template,
        account_activation_link=account_activation_link,
    )
    return task_response(
        "COMPLETED",
        f"Account activation email sent to {user.username}.",
        user_id=user_id,
    )


@shared_task(**default_task_params("send_activated_account_email"))
def send_activated_account_email(self, user_id: int):
    """Send email informing user that their account has been activated."""
    user = User.objects.get(id=user_id)

    subject = "Your account has been activated"
    template = "emails/users/activated-account.html"

    user.email_user(subject, template)
    return task_response(
        "COMPLETED",
        f"Activated account email sent to {user.username}.",
        user_id=user_id,
    )


@shared_task(**default_task_params("cleanup_expired_tokens", acks_late=True))
def cleanup_expired_tokens(self):
    """Delete expired tokens from database."""
    tokens = Token.objects.select_for_update().filter(expires_at__lt=timezone.now())
    num_deleted = tokens.delete()[0]
    return task_response(
        "COMPLETED",
        f"Deleted {num_deleted} expired tokens.",
        num_deleted=num_deleted,
    )


@shared_task(**default_task_params("cleanup_deactivated_users", acks_late=True))
def cleanup_deactivated_users(self):
    """Delete deactivated users from database."""
    expired_tokens = Token.objects.filter(
        expires_at__lt=timezone.now(),
        type=Token.TYPE_ACTIVATE_ACCOUNT,
    )
    users = (
        User.objects.select_for_update()
        .filter(is_active=False, tokens__in=expired_tokens)
        .distinct()
    )

    num_deleted = 0
    subject = "Your account has been deleted"
    template = "emails/users/account-deleted.html"

    for user in users.iterator():
        try:
            user.email_user(subject, template)
            num_deleted += user.delete()[0]
        except Exception:
            logger.exception("Error deleting user %s", user.username)
            continue

    return task_response(
        "COMPLETED",
        f"Deleted {num_deleted} deactivated users.",
        num_deleted=num_deleted,
    )
