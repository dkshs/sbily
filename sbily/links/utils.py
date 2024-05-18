import re

from django.contrib import messages
from django.core.validators import URLValidator

from .models import ShortenedLink

LINK_REGEX = r"^[a-zA-Z0-9_-]+$"
MAX_LINK_SIZE = 10


def link_is_valid(  # noqa: PLR0911
    request,
    original_link: str,
    shortened_link: str,
    link_id: str | None = None,
):
    links = ShortenedLink.objects.filter(shortened_link=shortened_link)
    if not original_link.strip():
        messages.error(request, "Please enter an original link")
        return False
    if not shortened_link.strip():
        messages.error(request, "Please enter a shortened link")
        return False
    if links.exclude(id=link_id).exists() if link_id else links.exists():
        messages.error(request, "Shortened link already exists")
        return False
    if not re.match(LINK_REGEX, shortened_link):
        messages.error(
            request,
            "Shortened link must only contain letters, numbers, underscores, and dashes",  # noqa: E501
        )
        return False
    if len(shortened_link.strip()) > MAX_LINK_SIZE:
        messages.error(request, "Shortened link must be 10 characters or less")
        return False
    validator = URLValidator()
    try:
        validator(original_link)
    except Exception:  # noqa: BLE001
        messages.error(request, "Invalid original link")
        return False
    return True
