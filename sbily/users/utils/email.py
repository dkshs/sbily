from django.core.mail import send_mail
from django.template.loader import render_to_string

from sbily.users.models import User


def send_email_to_user(user: User, subject: str, template: str, **kwargs):
    """Send an email to a user.

    Args:
        user: User object to send email to
        subject: Email subject line
        template: Email template to use
        **kwargs: Additional context data for the email template
    """
    if not all(
        [isinstance(user, User), isinstance(subject, str), isinstance(template, str)],
    ):
        msg = "Invalid argument types. Expected (User, str, str)"
        raise TypeError(msg)
    if not user.email:
        msg = "User does not have an email address"
        raise ValueError(msg)

    context = {"user": user, "name": user.get_short_name()}
    context.update(kwargs)

    message = render_to_string(template, context)
    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
        html_message=message,
    )
