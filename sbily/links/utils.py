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

    def validate_link_creation(is_temporary: bool) -> None:  # noqa: FBT001
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


def filter_dict(data: dict, exclude_keys: set) -> dict:
    """Remove specified keys from a dictionary.

    Args:
        data (dict): The original dictionary.
        exclude_keys (set): A set of keys to exclude from the dictionary.

    Returns:
        dict: The filtered dictionary without the specified keys.
    """
    return {k: v for k, v in data.items() if k not in exclude_keys}
