from celery import shared_task
from django.shortcuts import get_object_or_404

from .models import User


@shared_task(bind=True, name="send_welcome_email", max_retries=3)
def send_welcome_email(self, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        # name = user.first_name or user.username

        # subject = f"Welcome to Sbily, {name}!"
        # message = f"""
        #     Dear {name},

        #     Welcome to Sbily! We're excited to have you on board.

        #     Best regards,
        #     The Sbily Team
        # """
        # send_mail(
        #     subject=subject,
        #     message=message,
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[user.email],
        #     fail_silently=False,
        # )
    except Exception as exc:  # noqa: BLE001
        self.retry(exc=exc, countdown=60)  # Retry after 1 minute
        return {
            "status": "FAILED",
            "message": f"Failed to send welcome email to user {user_id}",
            "error": str(exc),
        }
    else:
        return {
            "status": "COMPLETED",
            "message": f"Welcome email sent to {user.username}",
            "user_id": user_id,
        }


@shared_task(bind=True, name="send_email_verification", max_retries=3)
def send_email_verification(self, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        # name = user.first_name or user.username

        # subject = f"Welcome to Sbily, {name}!"
        # message = f"""
        #     Dear {name},

        #     Welcome to Sbily! We're excited to have you on board.

        #     Best regards,
        #     The Sbily Team
        # """
        # send_mail(
        #     subject=subject,
        #     message=message,
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[user.email],
        #     fail_silently=False,
        # )
    except Exception as exc:  # noqa: BLE001
        self.retry(exc=exc, countdown=60)  # Retry after 1 minute
        return {
            "status": "FAILED",
            "message": f"Failed to send welcome email to user {user_id}",
            "error": str(exc),
        }
    else:
        return {
            "status": "COMPLETED",
            "message": f"Welcome email sent to {user.username}",
            "user_id": user_id,
        }
