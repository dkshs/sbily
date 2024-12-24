from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from sbily.users.models import User


def user_can_create_link(
    link_id: int,
    link_remove_at: datetime | None,
    user: User,
) -> None:
    """Checks if the user can create a new link or modify an existing link's temporary
    status according to their account permissions.

    Raises:
        ValidationError: If the user has reached the maximum number of links allowed
        for their account.
    """

    error_message = _(
        "You have reached the maximum number of links allowed for your account. "
        "Please upgrade your account to create more links.",
    )
    error_code = "max_links_reached"

    link = user.shortened_links.get(id=link_id) if link_id else None

    def validate_link_creation(**is_temporary: bool) -> None:
        if is_temporary and not user.can_create_temporary_link():
            raise ValidationError(error_message, code=error_code)
        if not is_temporary and not user.can_create_link():
            raise ValidationError(error_message, code=error_code)

    if link is None:
        validate_link_creation(is_temporary=link_remove_at is not None)
        return

    if (link_remove_at is not None) == (link.remove_at is not None):
        return

    validate_link_creation(is_temporary=link_remove_at is not None)
